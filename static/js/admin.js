

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

function countLinesIn(str) {
  if (!str) {
    return 0;
  }

  return str.split(/\r*\n/).length;
}
const flashes = document.querySelector('.flashes');

// If the flashes element exists
if (flashes) {
  setTimeout(function() {
    flashes.classList.add('hidden');
  }, 10000);
}
