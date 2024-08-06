import { streamGemini } from './gemini-api.js';

let form = document.querySelector('form');
let jobPositionInput = document.querySelector('input[name="job-position"]');
let cvUploadInput = document.querySelector('input[name="cv-upload"]');
let output = document.querySelector('.output');

form.onsubmit = async (ev) => {
  ev.preventDefault();
  output.innerHTML = '<p class="loading">Analyzing CV...</p>';  // Adding a loading message

  try {
    // Ensure the job position and CV are provided
    if (!jobPositionInput.value || !cvUploadInput.files.length) {
      output.innerHTML = '<p class="error">Please provide both the job position and a CV.</p>';
      return;
    }

    // Create a FormData object to hold the form data
    let formData = new FormData();
    formData.append('job-position', jobPositionInput.value);
    formData.append('cv-upload', cvUploadInput.files[0]);

    // Send the form data to the backend API
    let response = await fetch('/api/generate', {
      method: 'POST',
      body: formData
    });

    // Handle the response from the server
    if (!response.ok) {
      throw new Error(`Server error: ${response.statusText}`);
    }

    let data = await response.json();

    // Format the JSON output
    output.innerHTML = `<pre class="json-output">${JSON.stringify(data, null, 2)}</pre>`;
    
  } catch (e) {
    output.innerHTML = `<hr><p class="error">Error: ${e.message}</p>`;
  }
};
