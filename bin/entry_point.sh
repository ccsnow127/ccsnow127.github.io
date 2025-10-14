#!/bin/bash

CONFIG_FILE=_config.yml 

# Kill any stale jekyll from previous runs
jekyll_pid=$(pgrep -f jekyll) && kill -KILL $jekyll_pid 2>/dev/null || true

/bin/bash -c "rm -f Gemfile.lock && exec jekyll serve --watch --port=8080 --host=0.0.0.0 --livereload --livereload-port=35729 --verbose --trace --force_polling"&

while true; do

  inotifywait -q -e modify,move,create,delete $CONFIG_FILE

  if [ $? -eq 0 ]; then
 
    echo "Change detected to $CONFIG_FILE, restarting Jekyll"

    jekyll_pid=$(pgrep -f jekyll)
    kill -KILL $jekyll_pid

    /bin/bash -c "rm -f Gemfile.lock && exec jekyll serve --watch --port=8080 --host=0.0.0.0 --livereload --livereload-port=35729 --verbose --trace --force_polling"&

  fi

done
