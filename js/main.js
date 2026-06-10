document.addEventListener('DOMContentLoaded', () => {
  /* =========================================
     Scroll Reveal Animations
     ========================================= */
  const revealElements = document.querySelectorAll('.reveal-up');
  
  const revealCallback = (entries, observer) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('active');
        observer.unobserve(entry.target);
      }
    });
  };
  
  const revealObserver = new IntersectionObserver(revealCallback, {
    threshold: 0.1,
    rootMargin: "0px 0px -50px 0px"
  });
  
  revealElements.forEach(el => revealObserver.observe(el));
  /* =========================================
     Preloader Logic
     ========================================= */
  const preloader = document.getElementById('preloader');
  const videoElement = document.getElementById('preloader-video');
  const imagesContainer = document.getElementById('preloader-images-container');
  const maskHole = document.getElementById('video-mask-hole');
  
  if (preloader) {
    const hidePreloader = () => {
      if (!preloader.classList.contains('hidden')) {
        preloader.classList.add('hidden');
        const hero = document.querySelector('.hero');
        if (hero) hero.classList.add('expanded');
      }
    };

    const playImageSequence = () => {
      if (videoElement) videoElement.style.display = 'none';
      if (imagesContainer) {
        imagesContainer.style.display = 'block';
        const images = imagesContainer.querySelectorAll('.preload-img');
        
        // Preload images to ensure they are ready before the sequence starts
        images.forEach(img => {
          const preloaderImg = new Image();
          preloaderImg.src = img.src;
        });

        let currentIndex = 0;
        
        if (images.length > 0) {
          const showNextImage = () => {
            // We intentionally don't remove 'active' from previous images so the next image fades in smoothly on top, avoiding background flashes.

            if (currentIndex < images.length) {
              const img = images[currentIndex];
              img.classList.add('active');
              
              currentIndex++;
              // Flashes each image for 500ms like a rapid strobe
              setTimeout(showNextImage, 500); 
            } else {
              // Immediately reveal the hero video and start expansion
              const heroVideo = document.querySelector('.hero-bg-video');
              if (heroVideo) heroVideo.play();
              
              // Hard cut to the hero (removing preloader instantly)
              hidePreloader();
            }
          };
          showNextImage();
        } else {
          hidePreloader();
        }
      } else {
        hidePreloader();
      }
    };

    if (videoElement) {
      videoElement.playbackRate = 2.0; // Play twice as fast
      videoElement.addEventListener('ended', () => {
        setTimeout(playImageSequence, 1000);
      });
      // Fallback timeout in case the video fails to load or play
      setTimeout(() => {
        playImageSequence();
      }, 5000);
    } else {
      setTimeout(playImageSequence, 2000);
    }
  }

});
