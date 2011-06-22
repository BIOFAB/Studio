
/*
  TODO

  better error handling
  implement check to detect if drag-dropping is supported (and disable if not)
  implement check to detect if XHR file sending is supported (fall back if not):
    fallback to form-based upload in a hidden iframe, if multi-file supported
    fallback to single-file upload if not
  check if we can use the Blob API to combine multiple files into one before sending (for Safari)
*/

function MultiFileUpload() {

  /*
    Required arguments:
      callback: a function taking one argument, which will be in the following format:
        [{fileName: 'foo.txt',
          size: 1024, // bytes
          contentType: 'text/plain',
          content: 'GATCGATC...'}, // the actual file data
         ... ] // one of these hashes for each file
    
    Optional arguments:
      fileElementID: an input of type file
      dropElementID: the html element/node to activate drag
      // NOTE: either fileElement or dropElement or both must be supplied
      xhrBounceUrl: url to the server side bouncer accepting XHR style uploads
      classicBoundeUrl: url to the server side bouncer accepting classic multipart form uploads
      allowedContentTypes: an array of content types to allow
      allowedFileExtensions: an array of file extensions to allow
  */
    this.init = function(callback, fileElementID, dropElementID, xhrBounceUrl, classicBounceUrl, allowedContentTypes, allowedFileExtensions, gotNoAllowedCallback) {


      if(!fileElementID && !dropElementID) {
        alert('You need either a file element or a drop element in order for anything to happen');
        return;
      }

      if(!callback) {
        alert('MultiFileUpload needs you to specifiy a callback function in the constructor');
        return;
      }

    this.allowedContentTypes = allowedContentTypes || [];
    this.allowedFileExtensions = allowedFileExtensions || [];
    this.fileElementID = fileElementID;
    this.dropElementID = dropElementID;
    this.callback = callback;
    this.xhrBounceUrl = xhrBounceUrl;
    this.classicBounceUrl = classicBounceUrl;
    this.gotNoAllowedCallback = gotNoAllowedCallback;

    if(this.fileElementID) {
      $(this.fileElementID).addEventListener('change', this.onFileSelect.bindAsEventListener(this), false);
    }

    if(this.dropElementID) {
      $(this.dropElementID).addEventListener('dragover', this.onDragOver.bindAsEventListener(this), false);
      $(this.dropElementID).addEventListener('drop', this.onDrop.bindAsEventListener(this), false);
    }
    

  };

  // === end init ==

  this.supportsClientSideRead = function() {
    if(window.File && window.FileList && window.FileReader) {  
      return true;
    }
    return false;
  };
      
  this.supportsMultiFile = function() {
    
    // TODO need to check for XHR file upload ability
    if(window.File && window.FileList) {
      return true;
    }

  }; 

  this.supportedAPIList = function() {
    var sup = [];
    if(window.File) {
      sup.push('File');
    }
    if(window.FileReader) {
      sup.push('FileReader');
    }
    if(window.FileList) {
      sup.push('FileList');
    }
    if(window.Blob) {
      sup.push('Blob');
    }
    return sup;
  };


  // called after user browses for files and clicks "open" in the browse dialog
  this.onFileSelect = function(e) {
    var files = e.target.files; // FileList object
    files = this.filesAllowed(files);
    this.readFiles(files);
  };

  this.readFiles = function(files) {

    this.files = files;
    this.fileData = [];
    this.curFile = null;
    if(files.length > 0) {
      this.readFile(files[0]);
    } else {
      this.gotNoAllowedCallback();
    }
  };

  this.readFile = function(file) {
    if(!window.FileReader) {
      this.ajaxUploadRead(file);
    } else {
      this.clientSideRead(file);
    }    
  };


  this.finishedRead = function(fileObj) {
    this.fileData.push(fileObj);

    this.curFile = null;
    if(this.fileData.length >= this.files.length) {
      this.callback(this.fileData); // we are done. send the data to user specified callback
      this.files = []
      this.fileData = [];
    } else {
      // read the next file
      this.readFile(this.files[this.fileData.length]);
    }
  };

  this.onFinishClientSideRead = function(e) {
    var content = e.target.result;
    var fileObj = {
      fileName: this.curFile.name,
      size: this.curFile.size,
      contentType: this.curFile.type,
      content: content
    };
    this.finishedRead(fileObj);

  };

  this.clientSideRead = function(file) {
      var reader = new FileReader();
      reader.onload = this.onFinishClientSideRead.bindAsEventListener(this);
      reader.readAsText(file);
      this.curFile = file;
  };

  this.ajaxUploadStateChange = function() {
    if(this.xhr.readyState == 4) {
      if(this.xhr.status != 200) {
        // TODO better error handling
        alert('error uploading');
        this.curFile = null;
        return false;
      } else {
        this.finishedAjaxRead(this.xhr.responseText);
        this.curFile = null;
      }
    }
  };

  this.finishedAjaxRead = function(json) {
    var fileObj = json.evalJSON(true);
    this.finishedRead(fileObj);
  };

  this.ajaxUploadRead = function(file) {

    this.curFile = file;
    this.xhr = new XMLHttpRequest();
    var upload = this.xhr.upload;
    /*
    upload.onload = function() {
        alert('data sent');
    }
    */

    this.xhr.onreadystatechange = this.ajaxUploadStateChange.bindAsEventListener(this);

    this.xhr.open('POST', this.xhrBounceUrl, true);
    this.xhr.setRequestHeader("Content-Type", "multipart/form-data");  
    this.xhr.setRequestHeader("If-Modified-Since", "Mon, 26 Jul 1997 05:00:00 GMT");
    this.xhr.setRequestHeader("Cache-Control", "no-cache");
    this.xhr.setRequestHeader("X-Requested-With", "XMLHttpRequest");
    this.xhr.setRequestHeader("X-File-Name", file.name);
    this.xhr.setRequestHeader("X-File-Size", file.size);
    this.xhr.send(file);

  };


  // filter array of files, returning array
  // containing only allowed files according to allow rules
  this.filesAllowed = function(files) {

    // return full set of files if no allow rules are set
    if((this.allowedContentTypes.length == 0) && (this.allowedFileExtensions.length == 0)) {
      return files;
    }

    var allowedFiles = [];
    var i, j, allowed, curFile, curType, curExt, nameParts, extPart;    
    for(i=0; i < files.length; i++) {
        curFile = files[i];
        allowed = false;
        for(j=0; j < this.allowedContentTypes.length; j++) {
            curType = this.allowedContentTypes[j].toLowerCase();
            if(curFile.type.toLowerCase() == curType) {
                allowed = true;
            }
        }
        for(j=0; j < this.allowedFileExtensions.length; j++) {
            curExt = this.allowedFileExtensions[j].toLowerCase();
            nameParts = curFile.name.split('.');
            if(nameParts && (nameParts.length > 0)) {
              extPart = nameParts[nameParts.length - 1].toLowerCase();
              if(curExt == extPart) {
                allowed = true;
              }
            }
        }
        if(allowed) {
          allowedFiles.push(curFile);
        }
    }
    return allowedFiles;
  };

  /*
    drag drop code
  */

  this.onDrop = function(e) {
    e.stopPropagation();
    e.preventDefault();

    var files = e.dataTransfer.files;
    files = this.filesAllowed(files);
    this.readFiles(files);

  };

  this.onDragOver = function(e) {
    e.stopPropagation();
    e.preventDefault();
  };

}