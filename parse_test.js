const content = `What is the capital of France?
A) Paris
B) London
C) Berlin
D) Madrid`;

const lines = content.split('\n');
const textLines = [];
const options = [];

for (const line of lines) {
  const match = line.match(/^([A-D])\)\s*(.*)/i);
  if (match) {
    options.push({ key: match[1], text: match[2], full: line });
  } else {
    textLines.push(line);
  }
}

console.log("Text:", textLines.join('\n'));
console.log("Options:", options);
