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
  const photoShowcase = document.getElementById('preloader-photos');
  
  if (preloader) {
    const hidePreloader = () => {
      if (!preloader.classList.contains('hidden')) {
        preloader.classList.add('hidden');
        const hero = document.querySelector('.hero');
        if (hero) hero.classList.add('expanded');
        
        // Ensure the hero video plays when preloader hides
        const heroVideo = document.querySelector('.hero-bg-video');
        if (heroVideo) {
          heroVideo.currentTime = 0; // Restart so it perfectly syncs with the reveal
          const playPromise = heroVideo.play();
          if (playPromise !== undefined) {
            playPromise.catch(error => console.log("Autoplay prevented:", error));
          }
        }
      }
    };

    // iOS Autoplay Hack: Force play on first touch if blocked by browser policies
    document.addEventListener('touchstart', () => {
      if (videoElement && videoElement.paused) videoElement.play();
      const heroVideo = document.querySelector('.hero-bg-video');
      if (heroVideo && heroVideo.paused) heroVideo.play();
    }, { once: true });

    const runPhotoSequence = () => {
      // 1. Fade out the video
      if (videoElement) {
        videoElement.style.opacity = '0';
      }
      // 2. Trigger the cinematic zoom on the photos
      if (photoShowcase) {
        photoShowcase.classList.add('active-zoom');
      }
      
      const heroVideo = document.querySelector('.hero-bg-video');
      let minTimeElapsed = false;
      let videoReady = false;
      
      // 3. Minimum time the photos must be on screen (3.2s to allow sequence to finish)
      setTimeout(() => {
        minTimeElapsed = true;
        checkAndHide();
      }, 3200);
      
      // 4. Check if the homepage video is loaded
      if (heroVideo) {
        if (heroVideo.readyState >= 3) {
          videoReady = true;
        } else {
          heroVideo.addEventListener('canplay', () => {
            videoReady = true;
            checkAndHide();
          });
          // Fallback if video takes way too long or fails to load
          setTimeout(() => {
            videoReady = true;
            checkAndHide();
          }, 6000);
        }
      } else {
        videoReady = true;
      }
      
      const checkAndHide = () => {
        if (minTimeElapsed && videoReady) {
          hidePreloader();
        }
      };
      
      checkAndHide();
    };

    if (videoElement) {
      videoElement.playbackRate = 2.0; // Play twice as fast
      
      let sequenceStarted = false;
      videoElement.addEventListener('ended', () => {
        if (!sequenceStarted) {
          sequenceStarted = true;
          runPhotoSequence();
        }
      });
      
      // Fallback timeout in case the video fails to load or play
      setTimeout(() => {
        if (!sequenceStarted) {
          sequenceStarted = true;
          runPhotoSequence();
        }
      }, 5000);
    } else {
      setTimeout(hidePreloader, 2000);
    }
  }

});
