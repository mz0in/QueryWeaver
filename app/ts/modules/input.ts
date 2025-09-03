/**
 * Input handling module - textarea auto-resize functionality
 */

import { DOM } from "./config";

export function adjustTextareaHeight() {
  const textarea = DOM.messageInput;
  if (!textarea) return;

  // Reset height to auto to get the correct scrollHeight
  textarea.style.height = "auto";

  // Calculate the new height based on content
  const scrollHeight = textarea.scrollHeight;
  const maxHeight = parseInt(getComputedStyle(textarea).maxHeight);

  if (scrollHeight <= maxHeight) {
    // Content fits within max height, grow the textarea
    textarea.style.height = scrollHeight + "px";
    textarea.style.overflowY = "hidden";
  } else {
    // Content exceeds max height, set to max and enable scrolling
    textarea.style.height = maxHeight + "px";
    textarea.style.overflowY = "auto";
  }
}

export function setupTextareaAutoResize() {
  const textarea = DOM.messageInput;

  if (!textarea) return;

  // Adjust height on input
  textarea.addEventListener("input", adjustTextareaHeight);

  // Adjust height on paste
  textarea.addEventListener("paste", () => {
    // Use setTimeout to ensure the pasted content is processed
    setTimeout(adjustTextareaHeight, 0);
  });

  // Initial adjustment in case there's pre-filled content
  adjustTextareaHeight();
}
