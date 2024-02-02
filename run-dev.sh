# Start Backend
echo "Starting backend"

cd autogen-rag-server
source myenv/bin/activate
(script -q /dev/null python -u src/autogen-rag.py | awk '{print "[BACKEND] " $0}') & python_pid=$!
cd ..

# Start Frontend
echo "Starting frontend"

cd govuk-frontend-prototype
(script -q /dev/null npm run dev | awk '{print "[FRONTEND] " $0}') & npm_pid=$!
cd ..

# Kill child processes on kill signal
trap 'pkill -f autogen-rag.py; kill-9 $npm_pid' SIGINT

wait
