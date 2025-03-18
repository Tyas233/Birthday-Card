// Ambil elemen-elemen yang diperlukan
const cover = document.getElementById('cover');
const content = document.getElementById('content');
const openButton = document.getElementById('openButton');
const birthdayMusic = document.getElementById('birthdayMusic');
const submitMessageButton = document.getElementById('submitMessage');
const messageInput = document.getElementById('message');
const messageDisplay = document.getElementById('messageDisplay');

// Fungsi untuk membuka konten
openButton.addEventListener('click', () => {
    cover.classList.add('hidden'); // Sembunyikan cover
    content.classList.remove('hidden'); // Tampilkan konten
    birthdayMusic.play(); // Putar musik
});

// Fungsi untuk countdown
function updateCountdown() {
    const eventDate = new Date('March 18, 2025 13:00:00').getTime();
    const now = new Date().getTime();
    const timeLeft = eventDate - now;

    const days = Math.floor(timeLeft / (1000 * 60 * 60 * 24));
    const hours = Math.floor((timeLeft % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    const minutes = Math.floor((timeLeft % (1000 * 60 * 60)) / (1000 * 60));
    const seconds = Math.floor((timeLeft % (1000 * 60)) / 1000);

    document.getElementById('days').innerText = days;
    document.getElementById('hours').innerText = hours;
    document.getElementById('minutes').innerText = minutes;
    document.getElementById('seconds').innerText = seconds;
}

setInterval(updateCountdown, 1000);

// Fungsi untuk tombol "Simpan di Kalender"
document.querySelector('.calendar-button').addEventListener('click', () => {
    alert('Undangan telah disimpan di kalender Anda.');
});

// Fungsi untuk menambahkan pesan ke Local Storage dan menampilkannya
function addMessageToDisplay(message, isInitial = false) {
    const newMessage = document.createElement('p');
    newMessage.textContent = message;

    if (isInitial) {
        newMessage.classList.add('initial-message'); // Class untuk pesan awal
    } else {
        newMessage.classList.add('user-message'); // Class untuk pesan jawaban
    }

    // Sisipkan pesan di tengah
    const middleIndex = Math.floor(messageDisplay.children.length / 2);
    messageDisplay.insertBefore(newMessage, messageDisplay.children[middleIndex]);
}

// Fungsi untuk menyimpan pesan ke Local Storage
function saveMessageToLocalStorage(message) {
    let messages = JSON.parse(localStorage.getItem('messages')) || []; // Ambil pesan yang sudah ada
    messages.push(message); // Tambahkan pesan baru
    localStorage.setItem('messages', JSON.stringify(messages)); // Simpan kembali ke Local Storage
}

// Fungsi untuk memuat pesan dari Local Storage
function loadMessagesFromLocalStorage() {
    const messages = JSON.parse(localStorage.getItem('messages')) || [];
    messages.forEach((message) => {
        addMessageToDisplay(message); // Tampilkan pesan yang sudah disimpan
    });
}

// Fungsi untuk mengirim pesan
submitMessageButton.addEventListener('click', () => {
    const message = messageInput.value.trim();
    if (message) {
        saveMessageToLocalStorage(message); // Simpan pesan ke Local Storage
        addMessageToDisplay(message); // Tampilkan pesan di halaman
        messageInput.value = ''; // Kosongkan input
    } else {
        alert('Silakan tulis kesan dan pesanmu terlebih dahulu.');
    }
});

// Tampilkan pesan yang sudah disimpan saat halaman dimuat
window.addEventListener('load', () => {
    // Tampilkan pesan awal
    addMessageToDisplay('Pesan 1 (Pesan awal)', true);

    // Tampilkan pesan dari Local Storage
    loadMessagesFromLocalStorage();
});