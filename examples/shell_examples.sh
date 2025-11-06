# Example shell scripts using ffmcp

# Basic generation
ffmcp generate "Hello, world!"

# Process a file
ffmcp generate -i input.txt -o output.txt

# Chain with other tools
cat data.txt | ffmcp generate | grep "important" | wc -l

# Use in a script
RESULT=$(ffmcp generate "Translate: Hello" -p openai)
echo "Translation: $RESULT"

# Batch processing
for file in *.txt; do
    ffmcp generate -i "$file" -o "${file%.txt}_processed.txt"
done

