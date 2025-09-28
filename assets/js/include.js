// Carica header.html
fetch('header.html')
  .then(response => response.text())
  .then(data => {
    document.getElementById('site-header').innerHTML = data;
  });

// Carica footer.html
fetch('footer.html')
  .then(response => response.text())
  .then(data => {
    document.getElementById('site-footer').innerHTML = data;
    document.getElementById("year").textContent = new Date().getFullYear();
  });
