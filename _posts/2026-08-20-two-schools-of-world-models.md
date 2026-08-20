---
layout: post
title: Two Schools of World Models
date: 2026-08-20
description: Forty-seven papers, one entry each, with the original architecture figure — from ViT and DDPM through Genie, Cosmos, TRELLIS and pi-0. One school understands the world by generating it; the other by acting in it.
tags: world-models embodied-ai 3d-generation vla
categories: paper-notes
thumbnail: assets/img/world-models/genie.png
featured: true
toc:
  beginning: true
---

Every world model answers the same question — learn a dynamics you can condition on and roll out:

$$
p(s_{t+1} \mid s_{\le t},\, a_{\le t})
$$

The disagreement is never about that equation. It is about **what $$s$$ is** and **where the supervision comes from**. That single split produces two schools with different data, different backbones, different failure modes, and different companies.

|             | **Generative** (generate the world)                               | **Action-centric** (act in the world)                              |
| :---------- | :---------------------------------------------------------------- | :----------------------------------------------------------------- |
| Criterion   | Predicting or rendering the future = understanding                | Acting correctly = understanding                                   |
| State $$s$$ | Pixels, video latents, 3D geometry                                | Compact task-relevant features, often implicit                     |
| Supervision | Reconstruction, denoising, next-token — self-supervised           | Action supervision (BC), reward (RL)                               |
| Data        | Internet video, multi-view photos: abundant, **no action labels** | Teleop, real robots, sim: scarce, **with action labels**           |
| Backbone    | DiT, causal Transformer, RSSM                                     | VLM plus action expert                                             |
| Output      | Simulators, data engines, evaluators                              | A policy $$\pi$$                                                   |
| Weakness    | Drift, no physical guarantees, expensive                          | Narrow generalization, expensive data, no long-horizon imagination |

What follows is 47 papers, one entry each, grouped into eleven routes. Every entry has the same four blocks — **task and I/O**, **architecture and scale**, **training objective**, **why it is clever** — and closes with a one-line verdict. Every figure is the architecture figure from the original paper.

## 0 · Foundations — the shared parts bin

Nine pieces that both schools build out of. Every architecture diagram later in this post is some assembly of these; if this section is unfamiliar, the rest will not parse.

### ViT

_Google Research · 2020 · [arXiv:2010.11929](https://arxiv.org/abs/2010.11929) — An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale_

<div class="row justify-content-sm-center">
  <div class="col-sm-10 mt-3 mt-md-0">
    {% include figure.liquid path="assets/img/world-models/vit.png" class="img-fluid rounded z-depth-1" zoomable=true caption="Figure 1 of the original paper." %}
  </div>
</div>

**Task · I/O.** Images to class labels. Supervised pre-training on JFT-300M (300M images), then swap the head and fine-tune on smaller downstream sets.

**Architecture · scale.** Cut the image into 16x16 patches (196 tokens for a 224² image), prepend one `[class]` token, add learnable 1D position embeddings, feed a standard Transformer encoder. Base 86M / Large 307M / Huge 632M.

**Objective.** Plain classification cross-entropy. No contrastive learning, no masked reconstruction — deliberately nothing new.

**Why it is clever.** The real contribution is one crossing curve. A CNN hard-codes locality and translation equivariance into every layer: a free lunch when data is scarce, a ceiling when it is not. ViT loses on ImageNet, ties on ImageNet-21k, and overtakes on JFT-300M while using 2–4x less compute. The appendix goes further and shows that neither the `[class]` token nor 2D position embeddings are necessary.

> A prior is a crutch that guesses the answer for you while data is scarce; with enough data, guessing loses to learning.

### DDPM

_UC Berkeley · 2020 · [arXiv:2006.11239](https://arxiv.org/abs/2006.11239) — Denoising Diffusion Probabilistic Models_

<div class="row justify-content-sm-center">
  <div class="col-sm-10 mt-3 mt-md-0">
    {% include figure.liquid path="assets/img/world-models/ddpm.png" class="img-fluid rounded z-depth-1" zoomable=true caption="Figure 2 of the original paper." %}
  </div>
</div>

**Task · I/O.** Training: a noised image $$x_t$$ plus timestep $$t$$ to the noise $$\epsilon$$ that was added. Inference: start from pure noise and denoise for $$T=1000$$ steps.

**Architecture · scale.** A U-Net plus a timestep embedding and a few self-attention layers.

**Objective.** One line of MSE: $$\|\epsilon - \epsilon_\theta(x_t, t)\|^2$$. It is a reweighted variational bound, but the form is as simple as supervised regression.

**Why it is clever.** Split one-shot generation into a thousand denoising steps, each of which degenerates into easy regression. Training becomes extremely stable — there is no adversarial game to lose. Reparameterizing to predict the noise rather than the mean is the key to that stability.

> Almost every generative world model's training objective is a descendant of this one MSE.

### Latent Diffusion

_LMU Munich — the Stable Diffusion paper · 2021 · [arXiv:2112.10752](https://arxiv.org/abs/2112.10752) — High-Resolution Image Synthesis with Latent Diffusion Models_

<div class="row justify-content-sm-center">
  <div class="col-sm-10 mt-3 mt-md-0">
    {% include figure.liquid path="assets/img/world-models/latent-diffusion.png" class="img-fluid rounded z-depth-1" zoomable=true caption="Figure 3 of the original paper." %}
  </div>
</div>

**Task · I/O.** Text, layout or semantic map to image.

**Architecture · scale.** Two stages. (1) A VAE (KL- or VQ-regularized) downsamples the image 4–8x into a latent. (2) A U-Net diffusion model trained in that latent space, with conditioning injected by cross-attention.

**Objective.** Stage one: perceptual reconstruction plus an adversarial loss. Stage two: standard DDPM denoising in latent space. The two are trained separately.

**Why it is clever.** Separate perceptual compression from semantic compression. Most of the bits in an image are high-frequency detail nobody looks at — let the VAE absorb that, and let diffusion spend its capacity on semantics. An order of magnitude off the compute bill, which is the only reason video world models exist at all.

> World models are affordable because nobody runs diffusion on pixels.

### DiT

_Meta / NYU · 2022 · [arXiv:2212.09748](https://arxiv.org/abs/2212.09748) — Scalable Diffusion Models with Transformers_

<div class="row justify-content-sm-center">
  <div class="col-sm-10 mt-3 mt-md-0">
    {% include figure.liquid path="assets/img/world-models/dit.png" class="img-fluid rounded z-depth-1" zoomable=true caption="Figure 3 of the original paper." %}
  </div>
</div>

**Task · I/O.** Noisy latent plus timestep plus class condition to predicted noise.

**Architecture · scale.** Replace the U-Net wholesale with a pure Transformer: patchify the latent, run N DiT blocks. Three conditioning schemes are tried and adaLN-Zero (adaptive LayerNorm with zero-initialized residual branches) wins. XL/2 is about 675M.

**Objective.** Identical to DDPM — only the backbone changes, which is exactly where the paper's persuasive force comes from.

**Why it is clever.** Two things. adaLN-Zero beats cross-attention and in-context conditioning at almost no extra compute. And the paper hands over a clean Gflops-to-FID scaling law with no visible saturation. That curve is the entire justification for every video and 3D world model that came afterwards deciding to scale up.

> Sora, Kling, Cosmos and TRELLIS all run on this one diagram.

### Flow Matching

_Meta · 2022 · [arXiv:2210.02747](https://arxiv.org/abs/2210.02747) — Flow Matching for Generative Modeling_

<div class="row justify-content-sm-center">
  <div class="col-sm-10 mt-3 mt-md-0">
    {% include figure.liquid path="assets/img/world-models/flow-matching.png" class="img-fluid rounded z-depth-1" zoomable=true caption="Figure 3 of the original paper." %}
  </div>
</div>

**Task · I/O.** Noise to data. The network predicts a velocity field $$v(x,t)$$ rather than a noise vector.

**Architecture · scale.** The backbone is shared with diffusion verbatim (U-Net or DiT). Only the training objective and the sampler change.

**Objective.** Conditional flow matching: regress the vector field that transports noise onto data. Under an optimal-transport path, that trajectory is a straight line.

**Why it is clever.** Diffusion's noising path is curved, which is why sampling takes tens of steps. A straight OT path makes few-step and even one-step sampling viable, and lowers training variance along the way. Today's video models and VLA action experts have essentially all switched over.

> Same backbone, different objective, an order of magnitude faster sampling.

### VQ-VAE

_DeepMind · 2017 · [arXiv:1711.00937](https://arxiv.org/abs/1711.00937) — Neural Discrete Representation Learning_

<div class="row justify-content-sm-center">
  <div class="col-sm-10 mt-3 mt-md-0">
    {% include figure.liquid path="assets/img/world-models/vq-vae.png" class="img-fluid rounded z-depth-1" zoomable=true caption="Figure 1 of the original paper." %}
  </div>
</div>

**Task · I/O.** Image to a string of discrete codes (tokens) and back.

**Architecture · scale.** The encoder emits a continuous vector, which is replaced by its nearest neighbor in a learned codebook; the decoder reconstructs from the discrete code. Gradients are copied straight back to the encoder.

**Objective.** Three terms: reconstruction, a codebook loss pulling codes toward encodings, and a commitment loss pulling encodings toward codes.

**Why it is clever.** Nearest-neighbor lookup plus a straight-through estimator sidesteps the non-differentiability of discretization, and images become words for the first time. Genie's latent actions, GAIA-1's frame tokens and MAGVIT's video tokens are all built on this mechanism.

> Step one of translating a continuous world into a language.

### VQGAN

_Heidelberg University · 2020 · [arXiv:2012.09841](https://arxiv.org/abs/2012.09841) — Taming Transformers for High-Resolution Image Synthesis_

<div class="row justify-content-sm-center">
  <div class="col-sm-10 mt-3 mt-md-0">
    {% include figure.liquid path="assets/img/world-models/vqgan.png" class="img-fluid rounded z-depth-1" zoomable=true caption="Figure 2 of the original paper." %}
  </div>
</div>

**Task · I/O.** Image to a discrete token sequence, then an autoregressive Transformer that generates high-resolution images over those tokens.

**Architecture · scale.** VQ-VAE plus a patch discriminator and a perceptual loss, with a Transformer doing autoregression over the tokens.

**Objective.** Tokenizer side: reconstruction plus LPIPS plus adversarial. Transformer side: next-token cross-entropy.

**Why it is clever.** Pure L2 reconstruction is necessarily blurry at high compression ratios; trade it for a GAN loss and you buy back sharpness — which raises the compression ratio, which shortens the sequence enough for a Transformer to afford it. The division of labor is CNN for local texture, Transformer for global composition.

> A high-compression visual tokenizer is the entry ticket for autoregressive world models.

### NeRF

_UC Berkeley · 2020 · [arXiv:2003.08934](https://arxiv.org/abs/2003.08934) — NeRF: Representing Scenes as Neural Radiance Fields for View Synthesis_

<div class="row justify-content-sm-center">
  <div class="col-sm-10 mt-3 mt-md-0">
    {% include figure.liquid path="assets/img/world-models/nerf.png" class="img-fluid rounded z-depth-1" zoomable=true caption="Figure 2 of the original paper." %}
  </div>
</div>

**Task · I/O.** Multi-view photos plus camera poses to an MLP specific to that one scene. Query $$(x,y,z,\theta,\phi)$$ and get volume density and color.

**Architecture · scale.** An 8-layer MLP, about 1.5M parameters. Coordinates pass through a positional encoding — lifted onto high-frequency Fourier bases — before entering the network.

**Objective.** Volume-render along each ray into a pixel color and compare with the real photo under L2. Fully differentiable, with zero 3D supervision.

**Why it is clever.** Three ideas. Positional encoding fixes the MLP's innate low-frequency bias (remove it and everything blurs). Making color view-dependent is what allows specular highlights. And coarse-to-fine hierarchical sampling avoids spending samples on empty space.

> A 3D representation can be a function rather than a pile of data.

### 3DGS

_Inria · 2023 · [arXiv:2308.04079](https://arxiv.org/abs/2308.04079) — 3D Gaussian Splatting for Real-Time Radiance Field Rendering_

<div class="row justify-content-sm-center">
  <div class="col-sm-10 mt-3 mt-md-0">
    {% include figure.liquid path="assets/img/world-models/3dgs.png" class="img-fluid rounded z-depth-1" zoomable=true caption="Figure 2 of the original paper." %}
  </div>
</div>

**Task · I/O.** Multi-view photos plus an SfM point cloud to a set of 3D Gaussian ellipsoids that render novel views in real time.

**Architecture · scale.** Each Gaussian carries a position, a covariance (parameterized as quaternion plus scale), an opacity and spherical-harmonic color coefficients. Rendering is a tile-based differentiable rasterizer with depth-sorted alpha blending.

**Objective.** L1 plus D-SSIM between render and photo, with adaptive densification during training: clone or split Gaussians where gradients are large, prune the transparent ones.

**Why it is clever.** Swap the implicit MLP for explicit anisotropic ellipsoids and you keep differentiable optimization while gaining direct rasterization. Over 100 FPS at 1080p, beating NeRF on quality. The cost is storage.

> The default substrate for 3D world models: cheap, differentiable, editable.

---

## Part one · Generate the world

**The bet:** dynamics can be learned self-supervised from "predict the next frame / the next view", which means this school can consume internet-scale video with no action labels at all. Routes 1.1 through 1.5 run from the most virtual state representation to the most physical one.

## 1.1 · Video and latent world models

Keep the state in pixels or in a video latent, and learn dynamics by predicting the next frame. This is the route with the most data available and the least physical guarantee.

### Genie

_Google DeepMind · 2024 · [arXiv:2402.15391](https://arxiv.org/abs/2402.15391) — Genie: Generative Interactive Environments_

<div class="row justify-content-sm-center">
  <div class="col-sm-10 mt-3 mt-md-0">
    {% include figure.liquid path="assets/img/world-models/genie.png" class="img-fluid rounded z-depth-1" zoomable=true caption="Figure 2 of the original paper." %}
  </div>
</div>

**Task · I/O.** One prompt image plus one discrete action per step (8 choices) to the next frame. Trained on 30k hours of unlabeled 2D platformer video, with no action labels anywhere.

**Architecture · scale.** Three parts, all built on ST-Transformers (spatial attention alternating with causal temporal attention): a video tokenizer (VQ-VAE), a Latent Action Model (VQ-VAE with a codebook of size 8), and a MaskGIT-style dynamics model. 11B total, 10.1B of it dynamics.

**Objective.** Tokenizer reconstruction, plus the LAM reconstructing the next frame through an 8-code bottleneck, plus masked token prediction for dynamics.

**Why it is clever.** Make the action an 8-code bottleneck. The LAM wants to reconstruct the next frame and the only channel it has is those 8 codes, so it is forced to discover semantic actions like jump, left and right. At inference you swap the codes for player keypresses, and unlabeled video has become a playable world.

> Internet video became interaction data for the first time.

### GameNGen

_Google · 2024 · [arXiv:2408.14837](https://arxiv.org/abs/2408.14837) — Diffusion Models Are Real-Time Game Engines_

<div class="row justify-content-sm-center">
  <div class="col-sm-10 mt-3 mt-md-0">
    {% include figure.liquid path="assets/img/world-models/gamengen.png" class="img-fluid rounded z-depth-1" zoomable=true caption="Figure 3 of the original paper." %}
  </div>
</div>

**Task · I/O.** Past N frames plus past N actions to the next frame. Runs DOOM at 20 FPS on a single TPU.

**Architecture · scale.** Stable Diffusion v1.4, modified: text conditioning removed and replaced with action embeddings through cross-attention; encoded history frames concatenated channel-wise into the latent. Inference uses only 4 denoising steps.

**Objective.** Two stages: train an RL agent to play DOOM and collect trajectories, then train the conditional diffusion model on them with teacher forcing. The latent decoder is separately fine-tuned to fix the HUD digits.

**Why it is clever.** Noise augmentation is the whole ballgame. Noise the context frames during training and tell the model the noise level, and it learns to correct its own previous-frame errors. Without it, autoregressive rollout collapses within tens of frames.

> A neural network can be the game engine, not the renderer.

### Cosmos

_NVIDIA · 2025 · [arXiv:2501.03575](https://arxiv.org/abs/2501.03575) — Cosmos World Foundation Model Platform for Physical AI_

<div class="row justify-content-sm-center">
  <div class="col-sm-10 mt-3 mt-md-0">
    {% include figure.liquid path="assets/img/world-models/cosmos.png" class="img-fluid rounded z-depth-1" zoomable=true caption="Figure 4 of the original paper." %}
  </div>
</div>

**Task · I/O.** Video, optionally with text, actions or a camera trajectory, to future video. Positioned not as a product but as a data engine for robotics.

**Architecture · scale.** Two parallel lines: a diffusion WFM (DiT, 7B / 14B) and an autoregressive WFM (4B / 13B), both on an in-house Cosmos Tokenizer with continuous and discrete variants that are causal in time.

**Objective.** Denoising or flow for the diffusion line, next-token cross-entropy for the autoregressive one. Both do Text2World pre-training and then Video2World fine-tuning.

**Why it is clever.** The world model is unbundled into three products: Predict (forecast the future), Transfer (turn sim renders photoreal — domain randomization on steroids) and Reason (a physics-aware VLM for data curation and policy evaluation), wired into Omniverse, Isaac and GR00T as one pipeline.

> What is being sold is not a model, it is the data engine.

### Diffusion Forcing

_MIT · 2024 · [arXiv:2407.01392](https://arxiv.org/abs/2407.01392) — Diffusion Forcing: Next-token Prediction Meets Full-Sequence Diffusion_

<div class="row justify-content-sm-center">
  <div class="col-sm-10 mt-3 mt-md-0">
    {% include figure.liquid path="assets/img/world-models/diffusion-forcing.png" class="img-fluid rounded z-depth-1" zoomable=true caption="Figure 2 of the original paper." %}
  </div>
</div>

**Task · I/O.** Any sequence — video, trajectories, plans. Variable length, causal, indefinitely extensible.

**Architecture · scale.** A causal sequence model (RNN or Transformer). The one change that matters is that every token carries its own independent noise level.

**Objective.** Sample a noise level per token independently and denoise. That is effectively continuous partial masking, and it unifies teacher forcing (discrete, fully observed) with full-sequence diffusion (continuous, non-causal) in a single objective.

**Why it is clever.** Independent noise levels buy two things. Variable-length rollouts stop drifting, because a high-noise token is naturally treated as an uncertain future. And at sampling time you can pin future tokens at low noise to act as goal anchors, so the same model plans without retraining.

> Autoregression and diffusion are two sampling modes of the same model.

### GAIA-1

_Wayve · 2023 · [arXiv:2309.17080](https://arxiv.org/abs/2309.17080) — GAIA-1: A Generative World Model for Autonomous Driving_

<div class="row justify-content-sm-center">
  <div class="col-sm-10 mt-3 mt-md-0">
    {% include figure.liquid path="assets/img/world-models/gaia-1.png" class="img-fluid rounded z-depth-1" zoomable=true caption="Figure 2 of the original paper." %}
  </div>
</div>

**Task · I/O.** Video, text and ego actions (steering, speed) to future driving video. 9B parameters, 4,700 hours of UK urban driving.

**Architecture · scale.** Three stages: an image tokenizer (VQ, distilled against DINO features so tokens carry semantics), a 6.5B autoregressive Transformer world model, and a video diffusion decoder that turns tokens back into high-resolution video.

**Objective.** Next-token cross-entropy for the world model; the decoder is trained separately on diffusion denoising and temporal upsampling.

**Why it is clever.** Representation and rendering are fully decoupled. Semantics and dynamics live in autoregression over discrete tokens; image quality lives in the diffusion decoder. The world model never pays for pixel detail and can spend all of its capacity on what happens next.

> The first credible industrial world model — it generates dangerous scenarios that were never collected.

## 1.2 · Autoregressive token world models

Tokenize the world and run next-token prediction over it. The bet is that whatever made language models work is not specific to language.

### IRIS

_University of Geneva · 2022 · [arXiv:2209.00588](https://arxiv.org/abs/2209.00588) — Transformers are Sample-Efficient World Models_

<div class="row justify-content-sm-center">
  <div class="col-sm-10 mt-3 mt-md-0">
    {% include figure.liquid path="assets/img/world-models/iris.png" class="img-fluid rounded z-depth-1" zoomable=true caption="Figure 1 of the original paper." %}
  </div>
</div>

**Task · I/O.** Atari observation plus action to next-frame tokens, reward and done flag. Only 100k frames of real interaction are allowed, about two hours of play.

**Architecture · scale.** A discrete autoencoder (VQ-VAE, 16 tokens per frame) plus a GPT-style causal Transformer world model — only tens of millions of parameters.

**Objective.** Autoencoder reconstruction; the Transformer does next-token cross-entropy over an interleaved sequence of observation tokens and actions, and additionally predicts reward and termination.

**Why it is clever.** The policy is trained entirely inside imagination. The real environment is used only to collect data that improves the world model, and the agent never takes a learning step in it. RL's sample-efficiency problem becomes a sequence-modeling fitting problem.

> Two hours of real gameplay is enough to beat humans.

### MAGVIT-v2

_Google · 2023 · [arXiv:2310.05737](https://arxiv.org/abs/2310.05737) — Language Model Beats Diffusion - Tokenizer is Key to Visual Generation_

<div class="row justify-content-sm-center">
  <div class="col-sm-10 mt-3 mt-md-0">
    {% include figure.liquid path="assets/img/world-models/magvit-v2.png" class="img-fluid rounded z-depth-1" zoomable=true caption="Figure 7 of the original paper." %}
  </div>
</div>

**Task · I/O.** Image or video to discrete tokens and back; downstream, a language model generates over them.

**Architecture · scale.** A causal 3D CNN tokenizer that degenerates to an image tokenizer for a single frame. The core is Lookup-Free Quantization: codebook vectors are reduced to zero dimensions and a token is just the sign of each dimension, letting the codebook scale to $$2^{18}$$.

**Objective.** Reconstruction, perceptual and adversarial losses for the tokenizer; masked or autoregressive language modeling downstream.

**Why it is clever.** Ordinary VQ collapses as you scale the codebook — most codes go permanently unused. LFQ deletes the lookup entirely, and for the first time codebook size and reconstruction quality can both go up together.

> "LLMs lose to diffusion" was the tokenizer's fault, not autoregression's.

### Emu3

_BAAI · 2024 · [arXiv:2409.18869](https://arxiv.org/abs/2409.18869) — Emu3: Next-Token Prediction is All You Need_

<div class="row justify-content-sm-center">
  <div class="col-sm-10 mt-3 mt-md-0">
    {% include figure.liquid path="assets/img/world-models/emu3.png" class="img-fluid rounded z-depth-1" zoomable=true caption="Figure 1 of the original paper." %}
  </div>
</div>

**Task · I/O.** Text, images and video all tokenized into one sequence under next-token prediction. Generation and understanding share one set of weights.

**Architecture · scale.** A single decoder-only Transformer (8B) with a MoVQGAN-based visual tokenizer at 4x8x8 spatiotemporal compression.

**Objective.** Pure next-token cross-entropy. No diffusion, no CLIP, no bolted-on modules.

**Why it is clever.** Trained from scratch on mixed-modality sequences, it pushes "one vocabulary for three modalities" far enough to beat SDXL and LLaVA-1.6 — evidence that multimodality does not require a bespoke architecture per modality.

> The multimodal version of "next-token prediction is all you need".

## 1.3 · Compact latent-state world models

Give up on rendering the world and compress it into a small state that is only required to support control. The oldest branch, and still the most sample-efficient.

### World Models

_Google Brain — Ha & Schmidhuber · 2018 · [arXiv:1809.01999](https://arxiv.org/abs/1809.01999) — Recurrent World Models Facilitate Policy Evolution_

<div class="row justify-content-sm-center">
  <div class="col-sm-10 mt-3 mt-md-0">
    {% include figure.liquid path="assets/img/world-models/world-models.png" class="img-fluid rounded z-depth-1" zoomable=true caption="Figure 2 of the original paper." %}
  </div>
</div>

**Task · I/O.** Observation to action, validated on CarRacing and VizDoom.

**Architecture · scale.** Three parts: V, a VAE compressing frames to a 32-d $$z$$; M, an MDN-RNN predicting a mixture of Gaussians over the next $$z$$; and C, a linear controller with 867 parameters.

**Objective.** Reconstruction for V, maximum likelihood for M. C is not trained by gradients at all — it is evolved with CMA-ES.

**Why it is clever.** The controller is squeezed down to a few hundred parameters, because the world model has already compressed the world and the decision itself can be trivial. And the policy is trained entirely inside the dream, with a temperature parameter controlling how stochastic that dream is so the agent cannot exploit the world model's bugs.

> It named the field.

### DreamerV3

_DeepMind · 2023 · [arXiv:2301.04104](https://arxiv.org/abs/2301.04104) — Mastering Diverse Domains through World Models_

<div class="row justify-content-sm-center">
  <div class="col-sm-10 mt-3 mt-md-0">
    {% include figure.liquid path="assets/img/world-models/dreamerv3.png" class="img-fluid rounded z-depth-1" zoomable=true caption="Architecture figure from the original paper." %}
  </div>
</div>

**Task · I/O.** Observation plus action to latent state, latent state to action and value. 150+ tasks spanning Atari, DMLab, ProcGen and Minecraft.

**Architecture · scale.** RSSM: a deterministic GRU state $$h$$ plus a stochastic discrete state $$z$$, with an actor and a critic on top. Four sizes, 12M to 400M.

**Objective.** Three pieces: representation learning (reconstruction plus KL balancing), dynamics prediction, and actor-critic over imagined rollouts of horizon 15.

**Why it is clever.** symlog transforms, two-hot regression, KL balancing and free bits — a full toolkit for normalizing returns and observations of wildly different scales. The result is one hyperparameter set that clears every task, and the first agent to mine a diamond in Minecraft from scratch.

> The first world model that needed no per-task tuning.

### TD-MPC2

_UC San Diego · 2023 · [arXiv:2310.16828](https://arxiv.org/abs/2310.16828) — TD-MPC2: Scalable, Robust World Models for Continuous Control_

<div class="row justify-content-sm-center">
  <div class="col-sm-10 mt-3 mt-md-0">
    {% include figure.liquid path="assets/img/world-models/td-mpc2.png" class="img-fluid rounded z-depth-1" zoomable=true caption="Figure 3 of the original paper." %}
  </div>
</div>

**Task · I/O.** Observation plus action to latent state; at inference, plan online in latent space to emit actions. One 317M model covering 104 continuous-control tasks.

**Architecture · scale.** Encoder, latent dynamics, and reward / Q / policy-prior heads. Note what is missing: there is no decoder.

**Objective.** Never reconstruct the observation. Require only that the latent predicts reward and value under TD targets, so the latent retains only decision-relevant information.

**Why it is clever.** At inference, MPPI plans online in latent space and the policy prior merely supplies a sampling distribution. Model error accumulated during training gets corrected at inference by planning, which is why it is steadier than pure model-free methods.

> Decoder-free: a world model does not have to be able to see.

### V-JEPA 2

_Meta FAIR · 2025 · [arXiv:2506.09985](https://arxiv.org/abs/2506.09985) — V-JEPA 2: Self-Supervised Video Models Enable Understanding, Prediction and Planning_

<div class="row justify-content-sm-center">
  <div class="col-sm-10 mt-3 mt-md-0">
    {% include figure.liquid path="assets/img/world-models/v-jepa-2.png" class="img-fluid rounded z-depth-1" zoomable=true caption="Figure 1 of the original paper." %}
  </div>
</div>

**Task · I/O.** Video to representations; representations plus actions to future representations; given a goal image, plan an action sequence.

**Architecture · scale.** A 1B ViT-g encoder self-supervised on one million hours of internet video, plus V-JEPA 2-AC, a 300M action-conditioned prediction head trained on just 62 hours of Droid robot data.

**Objective.** Predict masked content in representation space against an EMA target encoder to prevent collapse — never reconstruct pixels. The AC head does teacher-forced and rollout latent prediction.

**Why it is clever.** Zero rewards, zero demonstrations. At inference you hand it a goal image, search actions with CEM inside the latent world model, and transfer zero-shot to unseen robots and scenes. This is the first real-robot closed loop for LeCun's no-pixel-generation position.

> Predicting representations instead of pixels is also enough to control a robot.

## 1.4a · Feed-forward 3D reconstruction

The state is explicit geometry, recovered from images in a single forward pass rather than by per-scene optimization.

### DUSt3R

_Naver Labs Europe · 2023 · [arXiv:2312.14132](https://arxiv.org/abs/2312.14132) — DUSt3R: Geometric 3D Vision Made Easy_

<div class="row justify-content-sm-center">
  <div class="col-sm-10 mt-3 mt-md-0">
    {% include figure.liquid path="assets/img/world-models/dust3r.png" class="img-fluid rounded z-depth-1" zoomable=true caption="Figure 2 of the original paper." %}
  </div>
</div>

**Task · I/O.** Two uncalibrated images to two pointmaps — a 3D coordinate per pixel, both expressed in the first image's frame. No intrinsics, no poses required.

**Architecture · scale.** Siamese ViT encoders, decoders with cross-attention, and regression heads (ViT-Large / Base). For many images, a global alignment stitches the pairwise pointmaps together.

**Objective.** Regression in 3D: confidence-weighted L2 with scale normalization.

**Why it is clever.** Replace the whole SfM/MVS pipeline with a single regression. Poses, depth and pixel correspondences all become by-products of the pointmap rather than prerequisites for it — which incidentally sidesteps the classic failure cases of textureless surfaces and wide baselines.

> 3D reconstruction goes from solving an optimization to running an inference.

### VGGT

_Oxford VGG / Meta · 2025 · [arXiv:2503.11651](https://arxiv.org/abs/2503.11651) — VGGT: Visual Geometry Grounded Transformer_

<div class="row justify-content-sm-center">
  <div class="col-sm-10 mt-3 mt-md-0">
    {% include figure.liquid path="assets/img/world-models/vggt.png" class="img-fluid rounded z-depth-1" zoomable=true caption="Figure 2 of the original paper." %}
  </div>
</div>

**Task · I/O.** 1 to 200 images to camera intrinsics and extrinsics, depth maps, pointmaps and 3D point tracks — all in one forward pass.

**Architecture · scale.** A 1.2B pure Transformer. DINOv2 tokenizes each image, then frame-wise self-attention and global self-attention alternate layer by layer.

**Objective.** Weighted multi-task regression against camera parameters, depth, pointmaps and tracks.

**Why it is clever.** The alternating attention is the whole paper: global attention enforces cross-image consistency, frame-wise attention preserves per-image detail. Stacking them alternately scales to 200 images without losing detail and without any geometric post-processing or bundle adjustment.

> One network swallows the entire geometric-vision toolbox.

### LRM

_Adobe Research / ANU · 2023 · [arXiv:2311.04400](https://arxiv.org/abs/2311.04400) — LRM: Large Reconstruction Model for Single Image to 3D_

<div class="row justify-content-sm-center">
  <div class="col-sm-10 mt-3 mt-md-0">
    {% include figure.liquid path="assets/img/world-models/lrm.png" class="img-fluid rounded z-depth-1" zoomable=true caption="Figure 1 of the original paper." %}
  </div>
</div>

**Task · I/O.** A single image to a NeRF in triplane form, in five seconds.

**Architecture · scale.** DINO ViT-B encodes the image; cross-attention projects image features onto triplane tokens; a Transformer triplane decoder feeds an MLP that outputs the NeRF. 500M parameters, trained on one million 3D assets from Objaverse and MVImgNet.

**Objective.** Rendering loss only: L2 plus LPIPS between rendered novel views and ground truth. No 3D shape supervision at all.

**Why it is clever.** Use the triplane as a token grid for 3D and Transformer scaling laws port straight into three dimensions. Single-image 3D goes from an hour of per-object optimization to a five-second forward pass.

> 3D generation's GPT moment.

## 1.4b · 3D and scene generation

Not recovering geometry from photographs but generating it — from a prompt, from one image, from a 2D prior that already knows more about 3D than it lets on.

### DreamFusion

_Google Research · 2022 · [arXiv:2209.14988](https://arxiv.org/abs/2209.14988) — DreamFusion: Text-to-3D using 2D Diffusion_

<div class="row justify-content-sm-center">
  <div class="col-sm-10 mt-3 mt-md-0">
    {% include figure.liquid path="assets/img/world-models/dreamfusion.png" class="img-fluid rounded z-depth-1" zoomable=true caption="Figure 3 of the original paper." %}
  </div>
</div>

**Task · I/O.** One text prompt to one NeRF, at roughly 1.5 hours of optimization per object.

**Architecture · scale.** No new network is trained: a frozen Imagen 2D diffusion model plus a randomly initialized NeRF (a modified Mip-NeRF 360).

**Objective.** Score Distillation Sampling: render the NeRF, add noise, let the frozen diffusion model predict the noise, and use (predicted minus true) noise directly as the gradient on NeRF parameters, bypassing the diffusion U-Net's Jacobian.

**Why it is clever.** Supervise a 3D representation with a 2D prior, using not a single piece of 3D training data. The costs are equally explicit — slow, the Janus multi-face problem, oversaturated colors — and those three defined the field's agenda for the next two years.

> You can generate 3D without any 3D data.

### Zero-1-to-3

_Columbia University · 2023 · [arXiv:2303.11328](https://arxiv.org/abs/2303.11328) — Zero-1-to-3: Zero-shot One Image to 3D Object_

<div class="row justify-content-sm-center">
  <div class="col-sm-10 mt-3 mt-md-0">
    {% include figure.liquid path="assets/img/world-models/zero-1-to-3.png" class="img-fluid rounded z-depth-1" zoomable=true caption="Figure 3 of the original paper." %}
  </div>
</div>

**Task · I/O.** One image plus a relative camera pose $$(R, T)$$ to the image from that viewpoint. Pipe it into SDS and you get full 3D.

**Architecture · scale.** Fine-tuned Stable Diffusion: condition on the input image's CLIP embedding concatenated with the pose, and channel-concatenate the input image itself into the UNet. Trained on paired views rendered from Objaverse.

**Objective.** Conditional diffusion denoising, with azimuth, elevation and distance deltas explicit in the condition.

**Why it is clever.** Large-scale 2D pre-training already contains 3D geometric priors — it just has no interface. This paper bolts a camera knob onto the diffusion model using synthetic data and unlocks it, reducing 3D generation to controllable novel-view synthesis.

> 2D diffusion models already understood 3D; they were only missing a knob.

### TRELLIS

_Microsoft Research / Tsinghua · 2024 · [arXiv:2412.01506](https://arxiv.org/abs/2412.01506) — Structured 3D Latents for Scalable and Versatile 3D Generation_

<div class="row justify-content-sm-center">
  <div class="col-sm-10 mt-3 mt-md-0">
    {% include figure.liquid path="assets/img/world-models/trellis.png" class="img-fluid rounded z-depth-1" zoomable=true caption="Figure 2 of the original paper." %}
  </div>
</div>

**Task · I/O.** Text or image to a mesh, 3D Gaussians, or a radiance field — one model, pick your output.

**Architecture · scale.** SLAT (Structured LATents): a sparse voxel grid storing only occupied positions, each active voxel carrying a DINOv2 feature vector. Two rectified-flow Transformer stages generate first the sparse structure and then the latents on it. 2B parameters, 500k assets.

**Objective.** Rectified flow, plus three independent decoders turning the same SLAT into 3DGS, a radiance field, or a mesh.

**Why it is clever.** Decouple geometric structure from appearance features into sparse structure plus dense features. Structure decides shape, features decide appearance, so one latent decodes into any 3D representation — and local editing falls out for free, since you can simply change some voxels.

> The mainstream paradigm for native 3D generation.

### Hunyuan3D 2.0

_Tencent Hunyuan · 2025 · [arXiv:2501.12202](https://arxiv.org/abs/2501.12202) — Hunyuan3D 2.0: Scaling Diffusion Models for High Resolution Textured 3D Assets Generation_

<div class="row justify-content-sm-center">
  <div class="col-sm-10 mt-3 mt-md-0">
    {% include figure.liquid path="assets/img/world-models/hunyuan3d-2-0.png" class="img-fluid rounded z-depth-1" zoomable=true caption="Figure 1 of the original paper." %}
  </div>
</div>

**Task · I/O.** Single image to a high-resolution mesh with PBR textures. Open source.

**Architecture · scale.** Two stages: Hunyuan3D-DiT for shape (a latent flow Transformer over a ShapeVAE, with importance sampling on the surface) and Hunyuan3D-Paint for multi-view-consistent PBR texture diffusion.

**Objective.** Flow matching for shape; multi-view diffusion conditioned on normal and position maps for texture.

**Why it is clever.** Shape and texture are fully separated — trained separately, scaled separately — with geometry maps acting as ControlNet-style conditions so textures never slide off the surface. That split is why both halves can iterate independently, and why the community has built so much on top of it.

> The de facto open-source base model for 3D asset generation.

## 1.4c · From viewable to interactable

The thinnest section here, and the most interesting one. A beautiful mesh is not an asset: it has no joints, no mass, no friction, no collision geometry. This route is about that gap.

### Articulate-Anything

_University of Michigan / NVIDIA · 2024 · [arXiv:2410.13882](https://arxiv.org/abs/2410.13882) — Articulate Anything: Automatic Modeling of Articulated Objects via a Vision-Language Foundation Model_

<div class="row justify-content-sm-center">
  <div class="col-sm-10 mt-3 mt-md-0">
    {% include figure.liquid path="assets/img/world-models/articulate-anything.png" class="img-fluid rounded z-depth-1" zoomable=true caption="Figure 2 of the original paper." %}
  </div>
</div>

**Task · I/O.** Text, an image or a video to an articulated URDF object: part hierarchy, joint types, axes and limits.

**Architecture · scale.** Nothing is trained. A VLM (Gemini or GPT) acts as a program synthesizer inside an actor-critic loop — the actor writes Python that builds the URDF, the critic renders it, compares against the input, and sends it back for a rewrite when it fails.

**Objective.** No gradients. Render-and-compare serves as the reward signal for self-correction.

**Why it is clever.** Turn modeling into coding: link placement and joint parameters are both expressible as programs, so the VLM's coding ability transfers directly. Success rate on PartNet-Mobility jumps from the prior state of the art of 8.7% to 75%.

> Generating 3D is not the hard part; generating 3D that moves is.

### URDFormer

_University of Washington · 2024 · [arXiv:2405.11656](https://arxiv.org/abs/2405.11656) — URDFormer: A Pipeline for Constructing Articulated Simulation Environments from Real-World Images_

<div class="row justify-content-sm-center">
  <div class="col-sm-10 mt-3 mt-md-0">
    {% include figure.liquid path="assets/img/world-models/urdformer.png" class="img-fluid rounded z-depth-1" zoomable=true caption="Architecture figure from the original paper." %}
  </div>
</div>

**Task · I/O.** One photo of a real scene to a complete URDF — part hierarchy, joint types, joint parameters — ready to load into a simulator.

**Architecture · scale.** Two Transformers: a global network predicting relations between objects, a local one predicting parts and joints. Trained on large-scale synthetic images.

**Objective.** Classification and regression over the parent-child relation matrix, joint types, and position and scale parameters.

**Why it is clever.** An inverted data pipeline. Rather than labeling real images, which is infeasible, take the layout of real images and reverse-generate a mass of synthetic images that come with complete URDF labels, then train a model that regresses URDF from image. Generation solves the annotation problem.

> Take a photo, get a room you can simulate.

### PhysGen

_UIUC · 2024 · [arXiv:2409.18964](https://arxiv.org/abs/2409.18964) — PhysGen: Rigid-Body Physics-Grounded Image-to-Video Generation_

<div class="row justify-content-sm-center">
  <div class="col-sm-10 mt-3 mt-md-0">
    {% include figure.liquid path="assets/img/world-models/physgen.png" class="img-fluid rounded z-depth-1" zoomable=true caption="Figure 2 of the original paper." %}
  </div>
</div>

**Task · I/O.** One image plus one user-specified force or torque, drawn as an arrow, to a physically correct video.

**Architecture · scale.** A training-free three-stage pipeline: perception (segmentation plus vision-language priors for mass, friction, restitution and normals), a real rigid-body physics engine for the trajectory, then rendering plus diffusion image editing for appearance and shadow completion.

**Objective.** No training objective — the system is assembled entirely from off-the-shelf models and a real physics engine.

**Why it is clever.** Give the dynamics to an actual physics engine and the appearance to a diffusion model, each doing what it is good at. The resulting video conserves momentum by construction and is genuinely controllable: change the input force and it re-solves rather than re-guesses.

> A video world model does not have to be end-to-end.

### EmbodiedGen

_Horizon Robotics · 2025 · [arXiv:2506.10600](https://arxiv.org/abs/2506.10600) — EmbodiedGen: Towards a Generative 3D World Engine for Embodied Intelligence_

<div class="row justify-content-sm-center">
  <div class="col-sm-10 mt-3 mt-md-0">
    {% include figure.liquid path="assets/img/world-models/embodiedgen.png" class="img-fluid rounded z-depth-1" zoomable=true caption="Figure 2 of the original paper." %}
  </div>
</div>

**Task · I/O.** Text or image to simulation-ready 3D assets and scenes, exported as URDF / MJCF / USD with real-world scale, collision geometry and physical properties.

**Architecture · scale.** A toolbox of six modules: image-to-3D, text-to-3D, texture generation, articulated object generation, scene layout generation, and real-scale and physical-property annotation.

**Objective.** Each module reuses its own generative objective; the system-level contribution is QA and export — watertighting, convex decomposition, scale calibration, simulatability checks.

**Why it is clever.** It productizes the grunt work between a good-looking mesh and a simulatable asset. That is exactly what route 1.4c is: not new generative capability, but the missing joint between generation and the physics engine.

> Upstream generation is crowded and downstream brains are crowded; this middle stretch is where the people aren't.

## 1.5 · Neural and physics hybrids

Instead of hoping a network learns conservation laws, keep the solver and make it learnable, or make it differentiable, or replace only the expensive part of it.

### GNS

_DeepMind · 2020 · [arXiv:2002.09405](https://arxiv.org/abs/2002.09405) — Learning to Simulate Complex Physics with Graph Networks_

<div class="row justify-content-sm-center">
  <div class="col-sm-10 mt-3 mt-md-0">
    {% include figure.liquid path="assets/img/world-models/gns.png" class="img-fluid rounded z-depth-1" zoomable=true caption="Figure 2 of the original paper." %}
  </div>
</div>

**Task · I/O.** A sequence of particle states — positions and velocities — to per-particle acceleration for the next step, integrated into a new state. Water, sand and goop all work.

**Architecture · scale.** Encoder-Processor-Decoder: build a graph over particles with edges within a radius, run 10 message-passing GNN layers, decode acceleration, integrate semi-implicitly.

**Objective.** L2 on single-step acceleration only. Nothing supervises the long trajectory.

**Why it is clever.** Two things. Noise injected into input positions during training simulates the error that accumulates during rollout, and it is the single key to long-horizon stability. And the inductive bias comes from the graph itself — local interactions, permutation invariance — so it extrapolates to tens of times more particles, unseen container shapes and unseen material combinations.

> A learned simulator can generalize instead of memorize.

### FNO

_Caltech · 2020 · [arXiv:2010.08895](https://arxiv.org/abs/2010.08895) — Fourier Neural Operator for Parametric Partial Differential Equations_

<div class="row justify-content-sm-center">
  <div class="col-sm-10 mt-3 mt-md-0">
    {% include figure.liquid path="assets/img/world-models/fno.png" class="img-fluid rounded z-depth-1" zoomable=true caption="Figure 1 of the original paper." %}
  </div>
</div>

**Task · I/O.** A PDE's initial or boundary condition function to the solution function. It is a map between functions, not between points.

**Architecture · scale.** A stack of Fourier layers: FFT, keep only low-frequency modes and multiply by learnable complex weights, inverse FFT, plus a pointwise linear transform and a nonlinearity.

**Objective.** Relative L2 regression against numerical solutions.

**Why it is clever.** The convolution theorem turns global convolution into pointwise multiplication in frequency space at $$O(n \log n)$$. More importantly the weights are defined on frequency modes rather than on the grid, so the operator is resolution-invariant: train at 128, infer at 1024, zero-shot — three orders of magnitude faster than a classical solver.

> It learns the operator — a whole family of PDEs — not one solution.

### DiffTaichi

_MIT CSAIL · 2019 · [arXiv:1910.00935](https://arxiv.org/abs/1910.00935) — DiffTaichi: Differentiable Programming for Physical Simulation_

<div class="row justify-content-sm-center">
  <div class="col-sm-10 mt-3 mt-md-0">
    {% include figure.liquid path="assets/img/world-models/difftaichi.png" class="img-fluid rounded z-depth-1" zoomable=true caption="Figure 2 of the original paper." %}
  </div>
</div>

**Task · I/O.** In: a simulation's control or initial parameters. Out: gradients of an objective with respect to them.

**Architecture · scale.** Not a network but a language and a compiler: source-to-source automatic differentiation on Taichi, with ten differentiable simulators averaging 75 lines of code each.

**Objective.** Any differentiable physical objective — "make this soft robot walk further" — differentiated straight through to the control parameters.

**Why it is clever.** A lightweight tape and checkpointing scheme designed for massively parallel, data-dependent memory access, which is the global read-write conflict endemic to physical simulation. On these control tasks gradient descent beats reinforcement learning by two orders of magnitude.

> If the physics engine is itself differentiable, you don't need a network to approximate it.

---

## Part two · Act in the world

**The bet:** you never have to draw the world. The world model can be a by-product of the policy, or exist only implicitly in its weights. Routes 2.1 (VLA), 2.2 (WAM) and 2.3 (hierarchical).

## 2.1 · VLA — vision, language, action

The world model is implicit, folded into a policy's weights. What is explicit is a vision-language backbone and a way of emitting actions from it.

### RT-2

_Google DeepMind · 2023 · [arXiv:2307.15818](https://arxiv.org/abs/2307.15818) — RT-2: Vision-Language-Action Models Transfer Web Knowledge to Robotic Control_

<div class="row justify-content-sm-center">
  <div class="col-sm-10 mt-3 mt-md-0">
    {% include figure.liquid path="assets/img/world-models/rt-2.png" class="img-fluid rounded z-depth-1" zoomable=true caption="Figure 1 of the original paper." %}
  </div>
</div>

**Task · I/O.** Image plus language instruction to a 7-DoF end-effector action: delta position, delta rotation, gripper.

**Architecture · scale.** PaLI-X (55B) or PaLM-E (12B) used directly as the backbone, architecture unchanged. Each action dimension is discretized into 256 bins that overwrite the least-used tokens in the vocabulary and are emitted as text.

**Objective.** Co-fine-tuning with web VQA data: half robot trajectories, half the original vision-language tasks.

**Why it is clever.** Actions are literally strings in the vocabulary, so web semantics carry over at zero cost, and co-fine-tuning prevents catastrophic forgetting. What you get back is emergent semantic generalization — it can follow "bring the coke to Taylor Swift", an instruction with no analogue in the training set.

> The first time a robot could use internet common sense.

### Diffusion Policy

_Columbia / TRI · 2023 · [arXiv:2303.04137](https://arxiv.org/abs/2303.04137) — Diffusion Policy: Visuomotor Policy Learning via Action Diffusion_

<div class="row justify-content-sm-center">
  <div class="col-sm-10 mt-3 mt-md-0">
    {% include figure.liquid path="assets/img/world-models/diffusion-policy.png" class="img-fluid rounded z-depth-1" zoomable=true caption="Figure 2 of the original paper." %}
  </div>
</div>

**Task · I/O.** The last two observation frames to the next 16 actions, of which only the first 8 are executed — a receding horizon.

**Architecture · scale.** A conditional diffusion model (1D CNN-UNet or Transformer) with a ResNet-18 visual encoder, BatchNorm swapped for GroupNorm. Small, under a hundred million parameters.

**Objective.** DDPM denoising, but the diffusion runs over action sequences rather than images. Observations are injected by FiLM rather than concatenation.

**Why it is clever.** Three ideas at once. Model the action distribution as multimodal, because regression averages "go around the left" and "go around the right" into "drive straight into it". Action chunking buys temporal consistency and responsiveness together. And position control beats velocity control. Average success rate across 15 tasks improves by 46.9%.

> Reframe action prediction from a regression problem into a generation problem.

### OpenVLA

_Stanford / Berkeley / Google · 2024 · [arXiv:2406.09246](https://arxiv.org/abs/2406.09246) — OpenVLA: An Open-Source Vision-Language-Action Model_

<div class="row justify-content-sm-center">
  <div class="col-sm-10 mt-3 mt-md-0">
    {% include figure.liquid path="assets/img/world-models/openvla.png" class="img-fluid rounded z-depth-1" zoomable=true caption="Figure 1 of the original paper." %}
  </div>
</div>

**Task · I/O.** Image plus language instruction to a 7-DoF action in 256 discrete bins. Trained on 970k Open X-Embodiment trajectories.

**Architecture · scale.** 7B: a Llama-2 7B language backbone with a dual vision tower concatenating DINOv2 (geometry) and SigLIP (semantics) features.

**Objective.** Cross-entropy over action tokens, overwriting the 256 least-used tokens in the vocabulary with action bins.

**Why it is clever.** The dual vision tower measurably beats a single tower — manipulation needs DINOv2-style geometric features and semantics alone are not enough. And it is fully open, with LoRA fine-tuning that fits on one consumer GPU. Seven times smaller than RT-2-X with a 16.5% higher success rate.

> The open-source VLA baseline, and academia's default starting point.

### pi-0

_Physical Intelligence · 2024 · [arXiv:2410.24164](https://arxiv.org/abs/2410.24164) — A Vision-Language-Action Flow Model for General Robot Control_

<div class="row justify-content-sm-center">
  <div class="col-sm-10 mt-3 mt-md-0">
    {% include figure.liquid path="assets/img/world-models/pi-0.png" class="img-fluid rounded z-depth-1" zoomable=true caption="Architecture figure from the original paper." %}
  </div>
</div>

**Task · I/O.** Multi-camera images, language and joint states to the next 50 continuous actions at 50 Hz. Pre-trained on 10k hours of cross-embodiment data.

**Architecture · scale.** A PaliGemma-3B VLM trunk plus a 300M action expert. They are really one Transformer with two sets of weights: image and text tokens use the VLM weights, state and action tokens use the action expert's.

**Objective.** Conditional flow matching — learn a vector field directly over continuous action chunks, with no discretization anywhere.

**Why it is clever.** Giving the action expert its own weights inherits the VLM's semantics without letting high-frequency action signals pollute the language representation. Flow matching is what makes 50 Hz continuous control possible at all; discrete tokens cannot. And the LLM pre-train / post-train recipe is carried over wholesale to robotics.

> It defined the modern VLA shape: VLM trunk plus action expert.

### GR00T N1

_NVIDIA · 2025 · [arXiv:2503.14734](https://arxiv.org/abs/2503.14734) — GR00T N1: An Open Foundation Model for Generalist Humanoid Robots_

<div class="row justify-content-sm-center">
  <div class="col-sm-10 mt-3 mt-md-0">
    {% include figure.liquid path="assets/img/world-models/gr00t-n1.png" class="img-fluid rounded z-depth-1" zoomable=true caption="Figure 2 of the original paper." %}
  </div>
</div>

**Task · I/O.** Image, language and proprioception to an action chunk. Cross-embodiment, one interface. 2.2B.

**Architecture · scale.** Two systems: System 2 is an Eagle-2 VLM (slow, semantics and planning) feeding System 1, a DiT action head (flow matching, fast, closed-loop control). Trained end-to-end jointly, communicating through latent tokens rather than text.

**Objective.** Flow matching on the action head, over training data organized as a data pyramid.

**Why it is clever.** The data pyramid is the real contribution: a base of massive human video pseudo-labeled with latent actions, a middle layer of simulation and neural-trajectory synthetic data, and only at the top the expensive real teleoperation. The two systems are not two calls to plan-then-execute; they are one differentiable whole.

> The public reference implementation of two systems plus a data pyramid.

## 2.2 · WAM — world models coupled to policies

The middle ground: predict the future and act, with the same weights or in the same loop, so that prediction becomes supervision for action.

### UniPi

_Google / MIT · 2023 · [arXiv:2302.00111](https://arxiv.org/abs/2302.00111) — Learning Universal Policies via Text-Guided Video Generation_

<div class="row justify-content-sm-center">
  <div class="col-sm-10 mt-3 mt-md-0">
    {% include figure.liquid path="assets/img/world-models/unipi.png" class="img-fluid rounded z-depth-1" zoomable=true caption="Figure 1 of the original paper." %}
  </div>
</div>

**Task · I/O.** Current observation plus a text task to a future video, then actions extracted from adjacent frames by an inverse dynamics model.

**Architecture · scale.** A text-conditioned video diffusion model imagining what to do, plus a small inverse dynamics model translating frames into actions.

**Objective.** Video diffusion denoising plus supervised regression for the IDM. The point is that the IDM needs very little action-labeled data.

**Why it is clever.** Split policy learning into imagine and translate. Video is an embodiment-agnostic representation, so the video generator can train on oceans of action-free video and the entire action-label burden falls on one small IDM. The data bottleneck is routed around.

> Video is the universal policy interface.

### UniSim

_UC Berkeley / Google DeepMind · 2023 · [arXiv:2310.06114](https://arxiv.org/abs/2310.06114) — Learning Interactive Real-World Simulators_

<div class="row justify-content-sm-center">
  <div class="col-sm-10 mt-3 mt-md-0">
    {% include figure.liquid path="assets/img/world-models/unisim.png" class="img-fluid rounded z-depth-1" zoomable=true caption="Figure 2 of the original paper." %}
  </div>
</div>

**Task · I/O.** Observation plus an action at any granularity — a text instruction, an end-effector pose, a camera motion — to the next observation.

**Architecture · scale.** A video diffusion model acting as an interactive simulator of the real world, jointly trained on internet video, robot data, navigation data and simulation, all unified into observation-action-observation format.

**Objective.** Action-conditioned video diffusion denoising.

**Why it is clever.** Different datasets are missing exactly complementary things: robot data has actions but no diversity, web video has diversity but no actions. A unified interface lets them be trained together and cover for each other. Policies trained inside it transfer zero-shot to real robots.

> A generative model as the game engine for the real world.

### GR-1

_ByteDance Research · 2023 · [arXiv:2312.13139](https://arxiv.org/abs/2312.13139) — Unleashing Large-Scale Video Generative Pre-training for Visual Robot Manipulation_

<div class="row justify-content-sm-center">
  <div class="col-sm-10 mt-3 mt-md-0">
    {% include figure.liquid path="assets/img/world-models/gr-1.png" class="img-fluid rounded z-depth-1" zoomable=true caption="Figure 1 of the original paper." %}
  </div>
</div>

**Task · I/O.** Language, image history and state to future images and actions, simultaneously.

**Architecture · scale.** A single GPT-style Transformer, pre-trained on Ego4D (large-scale human egocentric video) for video prediction, then fine-tuned on robot data with two output heads: image tokens and actions.

**Objective.** Pre-training: predict future frames given language and history. Fine-tuning: future-frame prediction and action regression together.

**Why it is clever.** One set of weights and one predict-the-future objective carry seamlessly from human video to robot actions. The architecture never changes; the action is just one more prediction head. The scarcer the robot data — at 10% of it — the larger the advantage from pre-training.

> Predicting the future is free action supervision.

### WorldVLA

_Alibaba Group · 2025 · [arXiv:2506.21539](https://arxiv.org/abs/2506.21539) — WorldVLA: Towards Autoregressive Action World Model_

<div class="row justify-content-sm-center">
  <div class="col-sm-10 mt-3 mt-md-0">
    {% include figure.liquid path="assets/img/world-models/worldvla.png" class="img-fluid rounded z-depth-1" zoomable=true caption="Figure 2 of the original paper." %}
  </div>
</div>

**Task · I/O.** Images, language and actions all tokenized into one autoregressive sequence.

**Architecture · scale.** A single autoregressive Transformer where the image and action tokenizers share a vocabulary. The world model (actions to images) and the action model (images to actions) are the same weights.

**Objective.** Bidirectional: next-image-token cross-entropy plus next-action-token cross-entropy, each regularizing the other.

**Why it is clever.** They find that autoregressing over action chunks accumulates error, and fix it with an attention mask that hides previously generated actions while generating the current one, forcing the model to look at images instead. Grasping success rate improves by 4–23%.

> The world model and the policy can be one set of weights.

## 2.3 · Hierarchical — an LLM planner over low-level skills

Train nothing. Let a frozen language model do the semantics and let a value function, a motion planner or a Python interpreter do the physics.

### SayCan

_Google / Everyday Robots · 2022 · [arXiv:2204.01691](https://arxiv.org/abs/2204.01691) — Do As I Can, Not As I Say: Grounding Language in Robotic Affordances_

<div class="row justify-content-sm-center">
  <div class="col-sm-10 mt-3 mt-md-0">
    {% include figure.liquid path="assets/img/world-models/saycan.png" class="img-fluid rounded z-depth-1" zoomable=true caption="Figure 1 of the original paper." %}
  </div>
</div>

**Task · I/O.** One long instruction — "I just worked out, can you bring me a drink and a snack?" — to a sequence of executable skills.

**Architecture · scale.** No large model is trained. The LLM scores each candidate skill for relevance to the task, a learned value function scores the same skill for whether it can be done right now, the two probabilities are multiplied, the argmax is executed, and the loop repeats.

**Objective.** Log-likelihood scoring on the frozen LLM side; an RL-learned value function on the affordance side.

**Why it is clever.** Separate can-say from can-do, then multiply them back together. The LLM supplies semantic plausibility and the value function supplies physical feasibility; drop either one and you get absurd plans, like sending the robot for an apple that is not in the room.

> The first time an LLM was wired to a real robot body.

### Code as Policies

_Google Research · 2022 · [arXiv:2209.07753](https://arxiv.org/abs/2209.07753) — Code as Policies: Language Model Programs for Embodied Control_

<div class="row justify-content-sm-center">
  <div class="col-sm-10 mt-3 mt-md-0">
    {% include figure.liquid path="assets/img/world-models/code-as-policies.png" class="img-fluid rounded z-depth-1" zoomable=true caption="Architecture figure from the original paper." %}
  </div>
</div>

**Task · I/O.** A natural-language instruction to executable Python policy code that calls perception and control APIs.

**Architecture · scale.** A frozen code LLM, a few few-shot examples, and a set of perception and control APIs — open-vocabulary detectors, motion primitives.

**Objective.** No training at all. Hierarchical code generation: when an undefined function is needed, recursively generate it.

**Why it is clever.** Code natively expresses loops, conditions and feedback. "Wipe the table back and forth until it's clean" is hard to say in language and is one `while` in code. And spatial reasoning can be delegated to a real library like NumPy instead of asking an LLM to do coordinate arithmetic in its head.

> A policy can be code rather than weights.

### VoxPoser

_Stanford · 2023 · [arXiv:2307.05973](https://arxiv.org/abs/2307.05973) — VoxPoser: Composable 3D Value Maps for Robotic Manipulation with Language Models_

<div class="row justify-content-sm-center">
  <div class="col-sm-10 mt-3 mt-md-0">
    {% include figure.liquid path="assets/img/world-models/voxposer.png" class="img-fluid rounded z-depth-1" zoomable=true caption="Figure 2 of the original paper." %}
  </div>
</div>

**Task · I/O.** Language instruction plus RGB-D to 3D value maps — affordance and constraint — then a trajectory from a motion planner.

**Architecture · scale.** Zero training: an LLM writes code that calls a VLM for open-vocabulary detection and segmentation, compiling language into score fields over a voxel grid, and then plans on that grid.

**Objective.** No training objective. Optionally, learn an online dynamics model from the generated trajectories for contact-rich tasks.

**Why it is clever.** The 3D value map is a universal interface between the LLM and the motion planner. The LLM never has to output precise joint angles, which it cannot do; it only has to say "stay away from this drawer, get close to that cup" and the planner does the rest. Which is why it needs zero robot training data.

> Open-vocabulary manipulation with zero robot data.

---

## The four-layer map

> **Assets** (Meshy · Tripo · Seed3D · Hunyuan3D · TRELLIS) → **Worlds and scenes** (World Labs · Genie · Cosmos · GAIA) → **Simulation and data** (Isaac · Genesis · MuJoCo · Lightwheel) → **Brains** (pi · GR00T · Gemini Robotics · Skild · Figure).

Counting papers per route is a crude instrument, but the count is suggestive. Route **1.4c** — turning a good-looking mesh into a simulatable asset — has four papers here, the fewest of any route, and it sits exactly between two crowded layers. Upstream, asset generation is a knife fight. Downstream, the robot-brain layer is full of well-funded labs. The stretch in between — add the joints, add mass and friction, add collision geometry, export a URDF that actually loads — is unglamorous, and it is where the map is emptiest.

## Four open questions

1. **Pixel prediction or representation prediction?** Generating pixels spends capacity on render-irrelevant detail — LeCun's objection, and V-JEPA 2 is the strongest evidence for it. But pixels remain the only self-supervised signal that scales to internet video.
2. **Implicit neural dynamics or explicit geometry plus a physics engine?** The former generalizes and conserves nothing; the latter is exact and cannot author the long tail. Route 1.4c is the attempt to have both.
3. **World model at training time or at inference time?** Train the policy inside imagination, which is cheap (IRIS, DreamerV3), or plan online with MPC, which self-corrects (TD-MPC2, V-JEPA 2)?
4. **Who owns evaluation?** If the world model is also the evaluator, what stops the two from being wrong in the same direction?

_These notes started life as a 53-slide deck built from the same source material; the route numbers (0, 1.1-1.5, 2.1-2.3) are that deck's taxonomy and are used consistently throughout._
