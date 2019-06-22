(function(){

    let root = this;

    /************************** below are dialog plugin codes **************************************/
    class DialogModalPlugin extends Phaser.Plugins.ScenePlugin {
        constructor (scene, pluginManager)
        {
            super(scene,pluginManager);

            if (!scene.sys.settings.isBooted) {
                scene.sys.events.once('boot', this.boot, this);
            }
        }
        init(opts){
            console.log('init');
            // Check to see if any optional parameters were passed
            if (!opts) opts = {};
            // set properties from opts object or use defaults
            this.borderThickness = opts.borderThickness || 3;
            this.borderColor = opts.borderColor || 0x907748;
            this.borderAlpha = opts.borderAlpha || 1;
            this.windowAlpha = opts.windowAlpha || 0.8;
            this.windowColor = opts.windowColor || 0x303030;
            this.windowHeight = opts.windowHeight || 150;
            this.padding = opts.padding || 32;
            this.closeBtnColor = opts.closeBtnColor || 'darkgoldenrod';
            this.dialogSpeed = opts.dialogSpeed || 3;

            // used for animating the text
            this.eventCounter = 0;

            // if the dialog window is shown
            this.visible = true;

            // the current text in the window
            this.text;

            // the text that will be displayed in the window
            this.dialog;
            this.graphics;
            this.closeBtn;

            // Create the dialog window
            this._createWindow();
        }
        // Creates the inner dialog window (where the text is displayed)
        _createInnerWindow(x, y, rectWidth, rectHeight) {
            this.graphics.fillStyle(this.windowColor, this.windowAlpha);
            this.graphics.fillRect(x + 1, y + 1, rectWidth - 1, rectHeight - 1);
        }

// Creates the border rectangle of the dialog window
        _createOuterWindow(x, y, rectWidth, rectHeight) {
            this.graphics.lineStyle(this.borderThickness, this.borderColor, this.borderAlpha);
            this.graphics.strokeRect(x, y, rectWidth, rectHeight);
        }
        // Creates the dialog window
        _createWindow() {
            const gameHeight = this._getGameHeight();
            const gameWidth = this._getGameWidth();
            const dimensions = this._calculateWindowDimensions(gameWidth, gameHeight);
            this.graphics = this.scene.add.graphics();
            this.graphics.depth=1000;

            this._createOuterWindow(dimensions.x, dimensions.y, dimensions.rectWidth, dimensions.rectHeight);
            this._createInnerWindow(dimensions.x, dimensions.y, dimensions.rectWidth, dimensions.rectHeight);
            this._createCloseModalButton();
            this._createCloseModalButtonBorder();
        }
        // Gets the width of the game (based on the scene)
        _getGameWidth() {
            return this.scene.sys.game.config.width;
        }

        // Gets the height of the game (based on the scene)
        _getGameHeight() {
            return this.scene.sys.game.config.height;
        }

        // Calculates where to place the dialog window based on the game size
        _calculateWindowDimensions(width, height) {
            const x = this.padding;
            const y = height - this.windowHeight - this.padding;
            const rectWidth = width - (this.padding * 2);
            const rectHeight = this.windowHeight;
            return {
                x,
                y,
                rectWidth,
                rectHeight
            };
        }
        // Creates the close dialog window button
        _createCloseModalButton() {
            let self = this;
            this.closeBtn = this.scene.make.text({
                x: this._getGameWidth() - this.padding - 15,
                y: this._getGameHeight() - this.windowHeight - this.padding + 2,
                text: '×',
                style: {
                    font: 'bold 12px Arial',
                    fill: this.closeBtnColor
                }
            });
            this.closeBtn.depth=1100;
            this.closeBtn.setInteractive();

            this.closeBtn.on('pointerover', function () {
                this.setTint(0xff0000);
            });
            this.closeBtn.on('pointerout', function () {
                this.clearTint();
            });
            this.closeBtn.on('pointerdown', function () {
                self.toggleWindow();
            });
        }

        // Creates the close dialog button border
        _createCloseModalButtonBorder() {
            let x = this._getGameWidth() - this.padding - 20;
            let y = this._getGameHeight() - this.windowHeight - this.padding;
            this.graphics.strokeRect(x, y, 20, 20);
        }

        setVisible(visible){
            if (this.timedEvent) this.timedEvent.remove();
            if (this.text) this.text.destroy();

            this.visible=visible;
            //if (this.text) this.text.visible = this.visible;
            if (this.graphics) this.graphics.visible = this.visible;
            if (this.closeBtn) this.closeBtn.visible = this.visible;
        }
        // Hide/Show the dialog window
        toggleWindow() {
            this.visible = !this.visible;
            if (this.text) this.text.visible = this.visible;
            if (this.graphics) this.graphics.visible = this.visible;
            if (this.closeBtn) this.closeBtn.visible = this.visible;
            if (this.timedEvent) this.timedEvent.remove();
            if (this.text) this.text.destroy();
        }


        // Sets the text for the dialog window
        setText(text, animate) {
            // Reset the dialog
            this.eventCounter = 0;
            this.dialog = text.split('');
            if (this.timedEvent) this.timedEvent.remove();

            let tempText = animate ? '' : text;
            this._setText(tempText);

            if (animate) {
                this.timedEvent = this.scene.time.addEvent({
                    delay: 150 - (this.dialogSpeed * 30),
                    callback: this._animateText,
                    callbackScope: this,
                    loop: true
                });
            }
        }

        // Slowly displays the text in the window to make it appear annimated
        _animateText() {
            this.eventCounter++;
            this.text.setText(this.text.text + this.dialog[this.eventCounter - 1]);
            if (this.eventCounter === this.dialog.length) {
                this.timedEvent.remove();
            }
        }

        // Calcuate the position of the text in the dialog window
        _setText(text) {
            // Reset the dialog
            if (this.text) this.text.destroy();

            let x = this.padding + 10;
            let y = this._getGameHeight() - this.windowHeight - this.padding + 5;

            this.text = this.scene.make.text({
                x,
                y,
                text,
                style: {
                    color:'#acacac',
                    wordWrap: { width: this._getGameWidth() - (this.padding * 2) - 25 }
                }
            });
            this.text.depth=1050;
        }

        boot() {
            let eventEmitter = this.systems.events;

            eventEmitter.on('shutdown', this.shutdown, this);
            eventEmitter.on('destroy', this.destroy, this);
        }

        //  Called when a Scene shuts down, it may then come back again later
        // (which will invoke the 'start' event) but should be considered dormant.
        shutdown() {
            if (this.timedEvent) this.timedEvent.remove();
            if (this.text) this.text.destroy();
        }

        // called when a Scene is destroyed by the Scene Manager
        destroy() {
            this.shutdown();
            this.scene = undefined;
        }
    }
    /**************************************-******************************************************/

    if (typeof exports !== 'undefined') {
        if (typeof module !== 'undefined' && module.exports) {
            exports = module.exports = DialogModalPlugin;
        }
        exports.DialogModalPlugin = DialogModalPlugin;
    } else if (typeof define !== 'undefined' && define.amd) {
        define('DialogModalPlugin', (function() { return root.DialogModalPlugin = DialogModalPlugin; })() );
    } else {
        root.DialogModalPlugin= DialogModalPlugin;
    }

    return DialogModalPlugin;

}).call(this);
