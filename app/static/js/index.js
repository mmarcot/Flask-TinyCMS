$(document).ready(function(){
    let slug = document.querySelector('form input[name="slug"]');
    let title = document.querySelector('form input[name="title"]');
    if(slug && title) {
        function convertToSlug(Text) {
            return Text
                .toLowerCase()
                .replace(/ /g,'-')
                .replace(/[^\w-]+/g,'')
                ;
        }
        slug.setAttribute('readonly', false);
        title.addEventListener('input', function(event) {
            slug.value = convertToSlug(title.value);
        });
    }

    let ace_editor_tag = document.getElementById('ace_editor');
    if(ace_editor_tag) {
        var editor = ace.edit("ace_editor");

        var textarea = $('textarea[name="content"]').hide();
        editor.getSession().setValue(textarea.val());
        editor.getSession().on('change', function(){
            textarea.val(editor.getSession().getValue());
        });
    
        var HtmlMode = ace.require("ace/mode/html").Mode;
        editor.session.setMode(new HtmlMode());
    }
});