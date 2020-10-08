
function NewsList() {

}

NewsList.prototype.listenSubmitEvent = function () {
    var submitBtn = $('.submit-btn');
    var textarea = $("textarea[name='comment']");
    submitBtn.click(function () {
        var content = textarea.val();
        var news_id = submitBtn.attr('data-news-id');
        xfzajax.post({
            'url': '/news/comment/add',
            'contentType': "application/json",
            'dataType': "json",
            'data':JSON.stringify({
                'content': content,
                'news_id': news_id
            }),
            'success': function (result) {
                console.log(result);
                if(result['code'] === 200){
                    console.log(result['data']);
                    var comment = result['data'];
                    var tpl = template('comment-item',{"comment":comment});
                    var commentListGroup = $(".comment-list");
                    commentListGroup.prepend(tpl);
                    window.messageBox.showSuccess('评论发表成功！');
                    textarea.val("");
                }else{
                    window.messageBox.showError(result['message']);
                }
            },
            'error': function (XMLHttpRequest, textStatus, errorThrown){
                console.log(textStatus);
                console.log(errorThrown);
            }
        });
    });
};

NewsList.prototype.run = function () {
    this.listenSubmitEvent();
};


$(function () {
    var newsList = new NewsList();
    newsList.run();
});