#!/bin/bash

# Get all commit hashes in reverse chronological order
commits=$(git log --reverse --pretty=format:"%H")

# Create a directory to store the commits
mkdir -p commit_history

# Counter for commit number
counter=1

# Loop through each commit
for commit in $commits; do
    echo "Checking out commit $counter: $commit"
    
    # Checkout the commit
    git checkout $commit
    
    # Create a directory for this commit
    commit_dir="commit_history/commit_${counter}_${commit:0:7}"
    mkdir -p "$commit_dir"
    
    # Copy all files to the commit directory
    cp -r * "$commit_dir" 2>/dev/null || true
    
    # Go back to the latest commit
    git checkout main
    
    ((counter++))
done

echo "All commits have been checked out and stored in commit_history directory" 