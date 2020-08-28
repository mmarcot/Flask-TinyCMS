$(document).ready(function(){
    // edit tags modal :
    $(".open-edit-tag-modal").click(function(){
        var tag_id = $(this).data('id');
        var tag_name = $(this).data('name');
        $('.modal-body #input-tag-id').val(tag_id);
        $('.modal-body #input-tag-name').val(tag_name);
    });
    $('#button-edit-tag').click(function() {
        var tag_id = $('.modal-body #input-tag-id').val();
        var tag_name = $('.modal-body #input-tag-name').val();
        
        var xhttp = new XMLHttpRequest();
        xhttp.onreadystatechange = function() {
            if (this.readyState == XMLHttpRequest.DONE && this.status == 200) {
                location.href = ADMIN_TAGS_URL;
            }
        };
        xhttp.open("POST", "/admin/tags/edit/" + tag_id, true);
        xhttp.setRequestHeader("Content-Type", "application/json");
        xhttp.send(JSON.stringify({
            post_type: 'edit_tag_name',
            tag_id: tag_id,
            tag_name: tag_name
        }));
    });
});