var getUrlParameter = function getUrlParameter(sParam) {
    var sPageURL = decodeURIComponent(window.location.search.substring(1)),
        sURLVariables = sPageURL.split('&'),
        sParameterName,
        i;

    for (i = 0; i < sURLVariables.length; i++) {
        sParameterName = sURLVariables[i].split('=');

        if (sParameterName[0] === sParam) {
            return sParameterName[1] === undefined ? true : sParameterName[1];
        }
    }
};

function onPageLoad(){
  $('#loadingModal').modal('show');
  $.get('/getUser', workflow);
};

function workflow(user){
  $('#loadingModal').modal('hide');
  if (user.isExists && user.isTermsSigned /*&& user.isTrialCreated*/){
    window.location.href= getUrlParameter('return');
  };
  if (!user.isExists){
    if (user.isCreateAllowed){
      $('#loadingModal').modal('show');
      $.get('/createUser', userCreated);
    }
    else {
      $.get('/getNotAllowedCreate', function(data){
        showNotAllowed(data);
      });
    }
  };
  if (user.isExists && !user.isTermsSigned){
    $('#loadingModal').modal('show');
    $.get('/getTerms', function(data){
      showTerms(user,data);
    });
  }
};

function userCreated(){
  $('#loadingModal').modal('hide');
  $.get('/getUser', workflow);
};

function showTerms(user, terms){
  $('#loadingModal').modal('hide');
  $('#termsText').html(terms.terms);
  $('#termsDiv').removeClass('hidden');
};
function showNotAllowed(markdown){
  $('#loadingModal').modal('hide');
  $('#sorryText').html(markdown.markdown);
  $('#sorryDiv').removeClass('hidden');
};
function signTerms(){
  $('#loadingModal').modal('show');
  $.get('/signTerms', function(){$.get('/getUser', workflow);});
};
