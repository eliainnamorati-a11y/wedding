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
        let currentIndex = 0;
        
        if (images.length > 0) {
          const showNextImage = () => {
            if (currentIndex < images.length) {
              const img = images[currentIndex];
              img.classList.add('active');
              
              // Start a smooth expansion from small to medium size (GPU Accelerated!)
              img.style.transition = 'transform 1.8s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.3s ease';
              void img.offsetWidth; // Force reflow
              img.style.transform = 'translate(-50%, -50%) scale(1)';
              
              currentIndex++;
              // Delay before the next image appears inside, creating concentric expanding borders
              setTimeout(showNextImage, 400); 
            } else {
              // The 3rd image has just started growing (takes 1800ms).
              // Wait 1400ms for it to almost finish growing, then fade out the preloader.
              setTimeout(() => {
                const heroVideo = document.querySelector('.hero-bg-video');
                if (heroVideo) heroVideo.play();
                
                // Fade out the preloader wrapper.
                // Since the .hero section underneath is currently cropped to the exact same 320x440 portrait hole,
                // this creates a perfect, seamless crossfade from the 3rd picture to the live hero video.
                preloader.style.transition = 'opacity 0.6s ease';
                preloader.style.opacity = '0';
                
                // Once the crossfade is complete, remove the preloader and let the .hero expand to full screen
                setTimeout(() => {
                  hidePreloader();
                  preloader.style.opacity = '';
                  preloader.style.transition = '';
                }, 600);
                
              }, 1400); 
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
