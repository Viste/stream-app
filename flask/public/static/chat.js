(function() {
    var Message;
  
    Message = function({
        text: text1,
        message_side: message_side1
      }) {
      this.text = text1;
      this.message_side = message_side1;
      this.draw = () => {
        var $message;
        $message = $($('.message_template').clone().html());
        $message.addClass(this.message_side).find('.text').html(this.text);
        $('.messages').append($message);
        return setTimeout(function() {
          return $message.addClass('appeared');
        }, 0);
      };
      return this;
    };
  
    $(function() {
      var getMessageText, message_side, sendMessage;
      message_side = 'right';
      getMessageText = function() {
        var $message_input;
        $message_input = $('.message_input');
        return $message_input.val();
      };
      sendMessage = function(text) {
        var $messages, message;
        if (text.trim() === '') {
          return;
        }
        $('.message_input').val('');
        $messages = $('.messages');
        message_side = message_side === 'left' ? 'right' : 'left';
        message = new Message({text, message_side});
        message.draw();
        return $messages.animate({
          scrollTop: $messages.prop('scrollHeight')
        }, 300);
      };
      $('.send_message').click(function(e) {
        return sendMessage(getMessageText());
      });
      $('.message_input').keyup(function(e) {
        if (e.which === 13) { // enter key
          return sendMessage(getMessageText());
        }
      });
      sendMessage('Hello Philip! :)');
      setTimeout(function() {
        return sendMessage('Hi Sandy! How are you?');
      }, 1000);
      return setTimeout(function() {
        return sendMessage('I\'m fine, thank you!');
      }, 2000);
    });
  
  }).call(this);