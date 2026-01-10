/**
 * Parse blocklet project metadata from Claude skill output
 * @param {string} output - Raw output from Claude containing the protocol markers
 * @returns {{title: string, description: string} | null} - Parsed metadata or null if not found
 */
function parseBlockletProject(output) {
  const match = output.match(/<<<BLOCKLET_PROJECT>>>\s*([\s\S]*?)\s*<<<END_BLOCKLET_PROJECT>>>/);
  if (!match) return null;
  try {
    return JSON.parse(match[1]);
  } catch {
    return null;
  }
}

// Test with sample output
const sample = `Perfect! This is a **static webapp** (Vite + React project). Let me emit the project metadata and continue with the conversion:

<<<BLOCKLET_PROJECT>>>
{"title": "Emoji Story Slots", "description": "An interactive emoji-based story slot game built with React and Vite"}
<<<END_BLOCKLET_PROJECT>>>

Now let me build the project:`;

const result = parseBlockletProject(sample);
console.log('Parsed result:', result);
