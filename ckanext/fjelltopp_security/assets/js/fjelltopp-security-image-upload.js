document.addEventListener('DOMContentLoaded', function() {
  // Store reference to original initialize function
  var originalInitialize = ckan.module.registry['image-upload'].prototype.initialize;

  // Override the initialize function
  ckan.module.registry['image-upload'].prototype.initialize = function() {
    // Call the original initialize
    originalInitialize.call(this);

    // Remove the URL button if it exists
    if (this.button_url) {
      this.button_url.remove();
    }

    // Update the fields storage to exclude button_url
    this.fields = $('<i />')
      .add(this.button_upload)
      .add(this.input)
      .add(this.field_url)
      .add(this.field_image);
  };
});