$(window).load(function(){
		jQuery(document).ready(function ($) {

			$('[data-popup-target]').click(function () {
				$('html').addClass('overlay');
				var activePopup = $(this).attr('data-popup-target');
				$(activePopup).addClass('visible');
				$(activePopup).addClass(overflow="scroll");
			});

			$(document).keyup(function (e) {
				if (e.keyCode == 27 && $('html').hasClass('overlay')) {
					clearPopup();
				}
			});

			$('.popup-exit').click(function () {
				clearPopup();

			});

			$('.popup-overlay').click(function () {
				clearPopup();
			});

			function clearPopup() {
				$('.popup.visible').addClass('transitioning').removeClass('visible');
				$('html').removeClass('overlay');

				setTimeout(function () {
					$('.popup').removeClass('transitioning');
				}, 200);
			}

		});
	});
	
threeSixtyPlayer.config.scaleFont = (navigator.userAgent.match(/msie/i)?false:true);
		threeSixtyPlayer.config.showHMSTime = true;

		// enable some spectrum stuffs

		threeSixtyPlayer.config.useWaveformData = true;
		threeSixtyPlayer.config.useEQData = true;

		// enable this in SM2 as well, as needed

		if (threeSixtyPlayer.config.useWaveformData) {
		  soundManager.flash9Options.useWaveformData = true;
		}
		if (threeSixtyPlayer.config.useEQData) {
		  soundManager.flash9Options.useEQData = true;
		}
		if (threeSixtyPlayer.config.usePeakData) {
		  soundManager.flash9Options.usePeakData = true;
		}

		if (threeSixtyPlayer.config.useWaveformData || threeSixtyPlayer.flash9Options.useEQData || threeSixtyPlayer.flash9Options.usePeakData) {
		  // even if HTML5 supports MP3, prefer flash so the visualization features can be used.
		  soundManager.preferFlash = true;
		}

		// favicon is expensive CPU-wise, but can be used.
		if (window.location.href.match(/hifi/i)) {
		  threeSixtyPlayer.config.useFavIcon = true;
		}

		if (window.location.href.match(/html5/i)) {
		  // for testing IE 9, etc.
		  soundManager.useHTML5Audio = true;
		}