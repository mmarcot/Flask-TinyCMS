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
});