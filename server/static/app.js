// Load image data from the backend...
async function renderImages() {
  function renderImageData(dataItems) {
    let html = '';
    for (const k in dataItems) {
      html = `${html}<li><span class="has-text-weight-bold">${k}:</span> ${dataItems[k]}</li>`;
    }

    return html;
  }

  const API_PREFIX = 'api';
  const imageResponse = await fetch(`/${API_PREFIX}/images`);
  const imageIds = await imageResponse.json();

  if (imageIds.length === 0) {
    // Unhide the notification
    const noImagesNotification = document.getElementById('noImagesNotification');
    noImagesNotification.classList.remove('is-hidden');
    return;
  }

  const imageArea = document.getElementById('imageArea');

  for (const imageId of imageIds) {
    const imageDetailResponse = await fetch(`${API_PREFIX}/data/${imageId}`)
    const imageData = await imageDetailResponse.json();
    const imageUrl = `/${API_PREFIX}/image/${imageId}`;
    const imageHTML = `
      <div class="card m-4">
        <div class="card-image">
          <figure class="image is-16by9">
            <img src="${imageUrl}" alt="Image ${imageId}">
          </figure>
        </div>
        <div class="card-content">
          <div class="media">
            <div class="media-content">
              <p class="title is-4">${new Date(parseInt(imageId * 1000, 10)).toUTCString()}</p>
            </div>
          </div>
    
          <div class="content">
            <ul>
              ${renderImageData(imageData)}
            </ul>
          </div>
        </div>
      </div>
    </div>`;

    imageArea.innerHTML = `${imageArea.innerHTML}${imageHTML}`;
  }
}

renderImages();