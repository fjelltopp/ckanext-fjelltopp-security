document.addEventListener('DOMContentLoaded', function() {
  const originalInitialize = ckan.module.registry['image-upload'].prototype.initialize;
  ckan.module.registry['image-upload'].prototype.initialize = function() {
    originalInitialize.call(this);
    if (this.button_url) {
      this.button_url.remove();
    }
    this.fields = $('<i />')
      .add(this.button_upload)
      .add(this.input)
      .add(this.field_url)
      .add(this.field_image);
  };
});