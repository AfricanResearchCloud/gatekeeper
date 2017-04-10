function onTermsAgreeClick(){
  var signingTerms = $.ajax({ type: 'POST', url: '/signTerms'});
  signingTerms.done(function(data){
    var content = $(data).find("#content");
  });
}
