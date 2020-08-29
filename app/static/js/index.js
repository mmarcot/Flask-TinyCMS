$(document).ready(function(){
    // edit tags modal :
    $(".open-edit-tag-modal").click(function(){
        var tag_id = $(this).data('id');
        var tag_name = $(this).data('name');
        $('.modal-body #input-tag-id').val(tag_id);
        $('.modal-body #input-tag-name').val(tag_name);
    });
});