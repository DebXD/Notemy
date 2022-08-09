(function($) {
    $.fn.passwordStrengthForcer = function(options) {
        if (this.attr('type') != 'password'){
            alert("Not a type=\"password\" field");
            return false;
        }
        var defaults = {
            minlength: 8,
            maxlength: 0, //0 means no max length
            numuppercaserequired: 1,
            numdigitsrequired: 1,
            numspecialrequired: 0,
            prettystatmap: {
                minlengthgood: "Minimum Length",
                maxlengthgood: "Maximum Length",
                uppercasegood: "Has Uppercase",
                digitsgood: "Has Digit",
                specialgood: "Has Special Character",
                good: '<b>good</b>',
                fail: '<b>fail</b>'
            }
        }
        var settings = $.extend({}, defaults, options);
        if (options.prettystatmap) {
            settings.prettystatmap = $.extend({}, defaults.prettystatmap, options.prettystatmap);
        }
        if (settings.maxlength > 0 && settings.minlength > settings.maxlength){
            alert("minlength: "+ settings.minlength + " is greater than maxlength: " + settings.maxlength);
            return false;
        }
        var checkvalue = function(val){
            var stats = {
                minlengthgood: false,
                maxlengthgood: false,
                uppercasegood: false,
                digitsgood: false,
                specialgood: false
            };

            if (val.length >= settings.minlength){
                stats.minlengthgood = true;
            }

            if (settings.maxlength <= 0 || val.length <= settings.maxlength){
                stats.maxlengthgood = true;
            }

            // Thanks https://stackoverflow.com/a/60696990/1993494
            var numupper = (val.match(/[A-Z]/g) || '').length;
            if (numupper >= settings.numuppercaserequired){
                stats.uppercasegood = true;
            }
            var numdigits = (val.match(/[\d]/g) || '').length;
            if (numdigits >= settings.numdigitsrequired){
                stats.digitsgood = true;
            }
            var numspecial = (val.match(/[:;<>?\/!@#$%^&*()_+\-={}\[\]\\|]/g) || '').length;
            if (numspecial >= settings.numspecialrequired){
                stats.specialgood = true;
            }
            return stats;
        }


        var $self = this;

        $self.on('input', function(){
            var val = $(this).val();
            var stats = checkvalue(val);
            var s = '';
            var numgood = 0;
            var numtotal = 0;
            for(var stat in stats){
                numtotal++;
                if (stats[stat]){
                    numgood++;
                }
                var key = stat;
                if (typeof(settings.prettystatmap[stat]) !== 'undefined'){
                    key = settings.prettystatmap[stat];
                }
                if (key == ''){
                    continue;
                }
                s += '<div>' + key + ': ';
                if (stats[stat] == true){
                    s += ' '+settings.prettystatmap.good;
                }else{
                    s += ' '+settings.prettystatmap.fail;
                }
                s += '</div>';
            }
            $psf = $(this).parent().find('.passwordStrengthForcer');
            if ($psf.length == 0){
                $(this).parent().append('<div class="passwordStrengthForcer">' + s + '</div>');
            }else{
                $psf.html(s);
            }
            $(this).attr('data-passwordStrengthForcer_AllGood', numgood === numtotal ? 1 : 0);
        });
    }
})(jQuery);
