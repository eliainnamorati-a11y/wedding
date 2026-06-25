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
        if (heroVideo) heroVideo.play();
      }
    };

    const runPhotoSequence = () => {
      // 1. Fade out the video
      if (videoElement) {
        videoElement.style.opacity = '0';
      }
      // 2. Trigger the cinematic zoom on the photos
      if (photoShowcase) {
        photoShowcase.classList.add('active-zoom');
      }
      
      // 3. Wait 2.5 seconds, then transition to homepage
      setTimeout(hidePreloader, 2500);
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
