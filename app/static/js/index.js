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
        let form_type = document.getElementById('form_type');
        if(form_type) {
            if (form_type.value == "post_create_form" || form_type.value == "page_create_form") {
                title.addEventListener('input', function(event) {
                    slug.value = convertToSlug(title.value);
                });
            }
            else if(form_type.value == "post_edit_form" || form_type.value == "page_edit_form") {
                slug.setAttribute('readonly', false);
            }
        }
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