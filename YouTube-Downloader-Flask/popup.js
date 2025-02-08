document.getElementById('downloadBtn').addEventListener('click', () => {
  const videoUrl = document.getElementById('videoUrl').value;
  
  if (videoUrl) {
    const flaskServerUrl = 'http://127.0.0.1:5000/formats';

    // POST isteği göndermek için
    fetch(flaskServerUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: new URLSearchParams({ url: videoUrl })
    })
    .then(response => response.text())
    .then(data => {
      document.body.innerHTML = data; // Gelen yanıtı göster
    })
    .catch(error => {
      console.error('Hata oluştu:', error);
    });
  } else {
    alert('Lütfen geçerli bir YouTube URL\'si girin.');
  }
});
