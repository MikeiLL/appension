function glitchErrorMessages(errors, evt) {
	var SELECTOR_ERRORS = $('#messages');
	if (errors.length > 0) {
		SELECTOR_ERRORS.empty();
		SELECTOR_ERRORS.addClass('errors');
		for (var i = 0, errorLength = errors.length; i < errorLength; i++) {
			SELECTOR_ERRORS.append(errors[i].message + '<br />');
		}
		SELECTOR_ERRORS.fadeIn(200);
		evt.preventDefault();
	} else {
		SELECTOR_ERRORS.css({ display: 'none' });
	}
}