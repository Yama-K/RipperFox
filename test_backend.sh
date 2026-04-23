#!/bin/bash

echo "=== RipperFox Backend Integration Test ==="
echo

# Test 1: Check if backend is running
echo "1. Testing backend connectivity..."
STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5100/api/status)
if [ "$STATUS" = "200" ]; then
    echo "✅ Backend is running (HTTP 200)"
    JOBS=$(curl -s http://localhost:5100/api/status | jq '. | length' 2>/dev/null || echo "0")
    echo "   Found $JOBS active jobs"
else
    echo "❌ Backend not responding (HTTP $STATUS)"
    echo "   Make sure your RipperFox backend is running on localhost:5100"
    exit 1
fi

echo

# Test 2: Check open-file endpoint
echo "2. Testing /api/open-file endpoint..."
OPEN_STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X POST -H "Content-Type: application/json" \
  -d '{"file_path":"/tmp/test.mp4"}' http://localhost:5100/api/open-file)

if [ "$OPEN_STATUS" = "200" ]; then
    echo "✅ /api/open-file endpoint implemented"
else
    echo "❌ /api/open-file endpoint not implemented (HTTP $OPEN_STATUS)"
    echo "   See yt_backend.py for implementation"
fi

echo

# Test 3: Check show-directory endpoint
echo "3. Testing /api/show-directory endpoint..."
DIR_STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X POST -H "Content-Type: application/json" \
  -d '{"dir_path":"/tmp"}' http://localhost:5100/api/show-directory)

if [ "$DIR_STATUS" = "200" ]; then
    echo "✅ /api/show-directory endpoint implemented"
else
    echo "❌ /api/show-directory endpoint not implemented (HTTP $DIR_STATUS)"
    echo "   See yt_backend.py for implementation"
fi

echo

# Test 4: Check job structure includes file_path
echo "4. Testing job structure..."
JOBS_DATA=$(curl -s http://localhost:5100/api/status)
if [ "$JOBS_DATA" != "{}" ] && [ "$JOBS_DATA" != "" ]; then
    echo "   Sample job data:"
    echo "$JOBS_DATA" | jq 'to_entries[0].value' 2>/dev/null || echo "   (Could not parse JSON - this is normal if no jobs exist)"
    HAS_FILE_PATH=$(echo "$JOBS_DATA" | jq 'to_entries[0].value.file_path' 2>/dev/null)
    if [ "$HAS_FILE_PATH" != "null" ] && [ -n "$HAS_FILE_PATH" ]; then
        echo "✅ Jobs include file_path field"
    else
        echo "⚠️  Jobs may not include file_path field (this is normal for old jobs)"
    fi
else
    echo "   No jobs to check (this is normal)"
fi

echo

# Summary
if [ "$OPEN_STATUS" = "200" ] && [ "$DIR_STATUS" = "200" ]; then
    echo "🎉 All backend endpoints are implemented!"
    echo "   The extension buttons should now work."
    echo
    echo "Next steps:"
    echo "1. Download a video using the extension"
    echo "2. Wait for it to show 'Done' status"
    echo "3. Click 'Open File' or 'Show in Directory' buttons"
else
    echo "⚠️  Backend implementation needed:"
    if [ "$OPEN_STATUS" != "200" ]; then
        echo "   - /api/open-file endpoint needs implementation"
    fi
    if [ "$DIR_STATUS" != "200" ]; then
        echo "   - /api/show-directory endpoint needs implementation"
    fi
    echo "   Check yt_backend.py for the implementation"
fi