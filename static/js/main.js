document.addEventListener('DOMContentLoaded', () => {

    // 1. Contador Animado para el Dashboard
    const counters = document.querySelectorAll('.stat-number');
    counters.forEach(counter => {
        const target = +counter.getAttribute('data-target');
        let count = 0;
        const speed = Math.max(1, Math.floor(target / 30));
        
        const updateCount = () => {
            if (count < target) {
                count += speed;
                if (count > target) count = target;
                counter.innerText = count;
                setTimeout(updateCount, 40);
            } else {
                counter.innerText = target;
            }
        };
        updateCount();
    });

    // 2. Sistema de Likes AJAX
    const likeButtons = document.querySelectorAll('.like-btn');
    likeButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const proyectoId = this.getAttribute('data-id');
            fetch(`/like_proyecto/${proyectoId}`, {
                method: 'POST'
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    this.querySelector('.like-count').innerText = data.likes;
                    this.style.transform = 'scale(1.2)';
                    setTimeout(() => { this.style.transform = 'scale(1)'; }, 200);
                }
            });
        });
    });

    // 3. Reproductor de Música Persistente entre Navegaciones
    const audio = document.getElementById('bg-music');
    const playBtn = document.getElementById('music-toggle');
    const musicSelect = document.getElementById('music-select');

    if (audio && playBtn) {
        audio.volume = 0.3; // Volumen moderado

        // A. Restaurar el estado guardado al cargar la nueva página
        const savedTrack = localStorage.getItem('bg_music_src');
        const savedTime = localStorage.getItem('bg_music_time');
        const isPlaying = localStorage.getItem('bg_music_playing') === 'true';

        if (savedTrack && musicSelect) {
            audio.src = savedTrack;
            musicSelect.value = savedTrack;
        }

        if (savedTime) {
            audio.currentTime = parseFloat(savedTime);
        }

        // Si estaba sonando antes de cambiar de página, reanuda automáticamente
        if (isPlaying) {
            audio.play().then(() => {
                playBtn.innerHTML = '⏸️';
            }).catch(error => {
                console.log('Autoplay bloqueado por el navegador hasta interactuar:', error);
                localStorage.setItem('bg_music_playing', 'false');
                playBtn.innerHTML = '🎵';
            });
        }

        // B. Guardar el segundo exacto y estado justo antes de salir de la página actual
        window.addEventListener('beforeunload', () => {
            localStorage.setItem('bg_music_time', audio.currentTime);
            localStorage.setItem('bg_music_playing', !audio.paused);
            if (musicSelect) {
                localStorage.setItem('bg_music_src', musicSelect.value);
            }
        });

        // C. Botón Play / Pausa
        playBtn.addEventListener('click', () => {
            if (audio.paused) {
                audio.play().then(() => {
                    playBtn.innerHTML = '⏸️';
                    localStorage.setItem('bg_music_playing', 'true');
                }).catch(error => {
                    console.error('Error al reproducir:', error);
                });
            } else {
                audio.pause();
                playBtn.innerHTML = '🎵';
                localStorage.setItem('bg_music_playing', 'false');
            }
        });

        // D. Selector de Canción
        if (musicSelect) {
            musicSelect.addEventListener('change', (e) => {
                const wasPlaying = !audio.paused;
                audio.src = e.target.value;
                localStorage.setItem('bg_music_src', e.target.value);
                localStorage.setItem('bg_music_time', 0); // Reinicia tiempo al cambiar pista

                if (wasPlaying) {
                    audio.play().then(() => {
                        playBtn.innerHTML = '⏸️';
                        localStorage.setItem('bg_music_playing', 'true');
                    });
                }
            });
        }
    }

    console.log("Sitio web oficial de Camila del Cielo v2.0 cargado correctamente ✨");
});
