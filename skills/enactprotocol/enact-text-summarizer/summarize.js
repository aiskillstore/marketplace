#!/usr/bin/env node

try {
  const text = process.argv[2] || '';

  // Word count
  const words = text.trim().split(/\s+/).filter(w => w.length > 0);
  const wordCount = words.length;

  // Character count (excluding spaces)
  const characterCount = text.replace(/\s/g, '').length;

  // Sentence count (rough estimation based on . ! ?)
  const sentences = text.split(/[.!?]+/).filter(s => s.trim().length > 0);
  const sentenceCount = sentences.length;

  // Average word length
  const totalWordLength = words.reduce((sum, word) => sum + word.length, 0);
  const averageWordLength = wordCount > 0 ? Number((totalWordLength / wordCount).toFixed(2)) : 0;

  // Reading time (average 200 words per minute)
  const readingTimeMinutes = Number((wordCount / 200).toFixed(2));

  const result = {
    wordCount,
    characterCount,
    sentenceCount,
    averageWordLength,
    readingTimeMinutes
  };

  console.log(JSON.stringify(result));
} catch (error) {
  console.log(JSON.stringify({
    error: `Failed to process text: ${error.message}`
  }));
  process.exit(1);
}
