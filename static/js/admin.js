

function copyTagContent(tagId) {
  // Get the text field
  var copyText = document.getElementById(tagId);

  // Select the text field
  copyText.select();
  copyText.setSelectionRange(0, 99999); // For mobile devices

   // Copy the text inside the text field
  navigator.clipboard.writeText(copyText.value);

  copyText.blur();
  copyText.selectionStart = copyText.selectionEnd;
}

const flashes = document.querySelector('.flashes');
console.log(`flashes: ${flashes}`)

// If the flashes element exists
if (flashes) {
  // Set a timeout to remove the flashes after 5 seconds
  setTimeout(function() {
    // Add the 'hidden' class to the flashes element
    flashes.classList.add('hidden');
  }, 10000);
}
