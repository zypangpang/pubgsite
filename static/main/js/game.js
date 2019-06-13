const config = {
    type: Phaser.WEBGL,
    width: 1600,
    height: 800,
    backgroundColor: '#42271a',
    //backgroundColor: '#244d1b',
    parent: 'phaser-example',
    physics: {
        default: 'arcade',
        arcade: {
            gravity: { y: 0 }
        }
    },
    scene: {
        preload: preload,
        create: create,
        update: update
    }
};

let game = new Phaser.Game(config);

const directions = {
    still:{offset:224,x:0,y:0,opposite:'still'},
    west: { offset: 0, x: -2, y: 0, opposite: 'east' },
    northWest: { offset: 32, x: -2, y: -1, opposite: 'southEast' },
    north: { offset: 64, x: 0, y: -2, opposite: 'south' },
    northEast: { offset: 96, x: 2, y: -1, opposite: 'southWest' },
    east: { offset: 128, x: 2, y: 0, opposite: 'west' },
    southEast: { offset: 160, x: 2, y: 1, opposite: 'northWest' },
    south: { offset: 192, x: 0, y: 2, opposite: 'north' },
    southWest: { offset: 224, x: -2, y: 1, opposite: 'northEast' }
};

let anims = {
    idle: {
        startFrame: 0,
        endFrame: 4,
        speed: 0.2
    },
    walk: {
        startFrame: 4,
        endFrame: 12,
        speed: 0.15
    },
    attack: {
        startFrame: 12,
        endFrame: 20,
        speed: 0.11
    },
    die: {
        startFrame: 20,
        endFrame: 28,
        speed: 0.2
    },
    shoot: {
        startFrame: 28,
        endFrame: 32,
        speed: 0.1
    }
};

let skeletons = [];

let tileWidthHalf;
let tileHeightHalf;

let d = 0;

let scene;

function preload ()
{
    let base_path='/static/main/';

    //this.load.image('sky', base_path+'assets/sky.png');

    this.load.json('map', base_path+'assets/isometric-grass-and-water.json');
    this.load.spritesheet('tiles', base_path+'assets/isometric-grass-and-water.png', { frameWidth: 64, frameHeight: 64 });
    this.load.spritesheet('skeleton', base_path+'assets/skeleton.png', { frameWidth: 128, frameHeight: 128 });
    this.load.image('house', base_path+'assets/rem_0002.png');
}
let water,grass;
function create ()
{
    scene = this;

    //this.add.image(400, 300, 'sky');

    grass=this.physics.add.staticGroup();
    water=this.physics.add.staticGroup();

    //  Our Skeleton class
    let Skeleton = new Phaser.Class({

        Extends: Phaser.GameObjects.Image,

        initialize:

        function Skeleton (scene, x, y, motion, direction)
        {
            this.x = x;
            this.y = y;

            this.motion = motion;
            this.anim = anims[motion];
            this.direction = directions[direction];
            this.speed = 0.15;
            this.f = this.anim.startFrame;
            this.destPoint=new Phaser.Geom.Point(x,y);
            //this.midPoint=this.destPoint;

            this.turn=false;


            Phaser.GameObjects.Image.call(this, scene, x, y, 'skeleton', this.direction.offset + this.f);

            this.depth = y + 64;

            //scene.time.delayedCall(this.anim.speed * 1000, this.changeFrame, [], this);
        },

        setDestination: function(x,y)
        {
            scene.time.removeAllEvents();
            this.motion='walk';
            this.turn=false;

            console.log('cur pos: '+this.x+','+this.y);
            console.log('dest pos: '+x+','+y);
            if(this.x===x&&this.y===y)
                return;
            this.destPoint=new Phaser.Geom.Point(x,y);
            this.anim=anims[this.motion];
            this.f = this.anim.startFrame;
            if(x>this.x)
                this.direction=directions['east'];
            else
                this.direction=directions['west'];
            if(y>this.y)
                this.direction=directions['south'];
            else
                this.direction=directions['north'];
            this.frame = this.texture.get(this.direction.offset + this.f);

            scene.time.delayedCall(this.anim.speed * 1000, this.changeFrame, [], this);
        },

        changeFrame: function ()
        {
            this.f++;

            let delay = this.anim.speed;

            if (this.f === this.anim.endFrame)
            {
                //scene.time.removeAllEvents();
                switch (this.motion)
                {
                    case 'walk':
                        this.f = this.anim.startFrame;
                        this.frame = this.texture.get(this.direction.offset + this.f);
                        scene.time.delayedCall(delay * 1000, this.changeFrame, [], this);
                        break;

                    case 'attack':
                        delay = Math.random() * 2;
                        scene.time.delayedCall(delay * 1000, this.resetAnimation, [], this);
                        break;

                    case 'idle':
                        //delay = 0.5 + Math.random();
                        //scene.time.delayedCall(delay * 1000, this.resetAnimation, [], this);
                        break;

                    case 'die':
                        delay = 6 + Math.random() * 6;
                        scene.time.delayedCall(delay * 1000, this.resetAnimation, [], this);
                        break;
                }
            }
            else
            {
                this.frame = this.texture.get(this.direction.offset + this.f);

                scene.time.delayedCall(delay * 1000, this.changeFrame, [], this);
            }
        },

        resetAnimation: function ()
        {
            this.f = this.anim.startFrame;

            this.frame = this.texture.get(this.direction.offset + this.f);

            scene.time.delayedCall(this.anim.speed * 1000, this.changeFrame, [], this);
        },

        update: function ()
        {
            if (this.motion === 'walk')
            {
                //console.log('pos: '+this.x+' '+this.y);


                //  Walked far enough?
                //if (Phaser.Math.Distance.Between(this.startX, this.startY, this.x, this.y) >= this.distance)
                let roundX=Math.round(this.x);
                let roundY=Math.round(this.y);
                if(roundX===this.destPoint.x&&roundY===this.destPoint.y )
                {
                        this.direction = directions['still'];
                        this.anim=anims['idle'];
                        this.f = this.anim.startFrame;
                        this.frame = this.texture.get(this.direction.offset + this.f);
                        //this.startX = this.x;
                        //this.startY = this.y;
                    return;
                }
                if(!this.turn) {
                    if (roundX === this.destPoint.x) {
                        if (roundY < this.destPoint.y)
                            this.direction = directions['south'];
                        else
                            this.direction = directions['north'];

                        this.anim = anims['walk'];
                        this.f = this.anim.startFrame;
                        this.frame = this.texture.get(this.direction.offset + this.f);
                        this.trun = true;
                    } else if (roundY === this.destPoint.y) {
                        if (roundX < this.destPoint.x)
                            this.direction = directions['east'];
                        else
                            this.direction = directions['west'];

                        this.anim = anims['walk'];
                        this.f = this.anim.startFrame;
                        this.frame = this.texture.get(this.direction.offset + this.f);
                        this.turn = true;
                    }
                }

                this.x += this.direction.x * this.speed;

                //if (this.direction.y !== 0)
                //{
                    this.y += this.direction.y * this.speed;
                    this.depth = this.y + 64;
                //}
            }
        }

    });

    buildMap();
    placeHouses();

    skeletons.push(this.add.existing(new Skeleton(this, 240, 290, 'idle', 'still')));

    skeletons.push(this.add.existing(new Skeleton(this, 760, 100, 'idle', 'still')));
    skeletons.push(this.add.existing(new Skeleton(this, 800, 140, 'attack', 'northWest')));


    this.cameras.main.setSize(1600, 1200);

    this.input.on('pointerdown',function (pointer) {
        console.log(pointer.x,pointer.y);
        skeletons[0].setDestination(pointer.x,pointer.y)
    },this);

    // this.cameras.main.scrollX = 800;
}

/*function myBuildMap()
{
    const map = scene.make.tilemap({ key: "map" });

    // Parameters are the name you gave the tileset in Tiled and then the key of the tileset image in
    // Phaser's cache (i.e. the name you used in preload)
    const tileset = map.addTilesetImage("isometric_grass_and_water", "tiles");

    // Parameters: layer name (or index) from Tiled, tileset, x, y
    const Layer = map.createStaticLayer("Tile Layer 1", tileset, 0, 0);
}*/

let centerX,centerY;
function checkCollides(prpty) {
    return prpty.name==='collides' && prpty.value===true;
}
function buildMap ()
{
    //  Parse the data out of the map
    const data = scene.cache.json.get('map');

    const tilewidth = data.tilewidth;
    const tileheight = data.tileheight;

    tileWidthHalf = tilewidth / 2;
    tileHeightHalf = tileheight / 2;

    const layer = data.layers[0].data;
    const tilesets= data.tilesets[0].tiles;

    const mapwidth = data.layers[0].width; //tile count
    const mapheight = data.layers[0].height;//tile count

    centerX = mapwidth * tileWidthHalf; //pixel
    centerY = 20; //pixel

    let i = 0;

    for (let y = 0; y < mapheight; y++)
    {
        for (let x = 0; x < mapwidth; x++)
        {
            const id = layer[i] - 1;

            let tx = (x - y) * tileWidthHalf;
            let ty = (x + y) * tileHeightHalf;
            let tile;
            if(tilesets[id].properties.find(checkCollides))
            {
                //let tile = scene.add.image(centerX + tx, centerY + ty, 'tiles', id);
                tile = water.create(centerX + tx, centerY + ty, 'tiles', id);
            }
            else
            {
                tile = grass.create(centerX + tx, centerY + ty, 'tiles', id);
            }

            tile.depth = centerY + ty;

            i++;
        }
    }
}
function getCenterXYFromTileCoord(tx,ty) {
    let tmpPos=new Phaser.Geom.Point();
    tmpPos.x=centerX+(tx-ty)*tileWidthHalf;
    tmpPos.y=centerY+(tx+ty)*tileHeightHalf;
    return tmpPos;
}

function placeHouses ()
{
    let tmpPos=getCenterXYFromTileCoord(2,21);
    let house = scene.add.image(tmpPos.x,tmpPos.y, 'house');
    //let house = scene.add.image(240, 370, 'house');

    house.depth = house.y + 86;

    house = scene.add.image(1300, 290, 'house');

    house.depth = house.y + 86;
}
let first=true;

function update ()
{
    /*if(first)
    {
        skeletons[0].setDestination(400,300);
        skeletons[1].setDestination(600,400);
        first=false;
    }*/
    skeletons.forEach(function (skeleton) {
        skeleton.update();
    });

    // return;

    /*if (d)
    {
        this.cameras.main.scrollX -= 0.5;

        if (this.cameras.main.scrollX <= 0)
        {
            d = 0;
        }
    }
    else
    {
        this.cameras.main.scrollX += 0.5;

        if (this.cameras.main.scrollX >= 800)
        {
            d = 1;
        }
    }*/
}

function cartesianToIsometric(cartPt){
    var tempPt=new Phaser.Point();
    tempPt.x=cartPt.x-cartPt.y;
    tempPt.y=(cartPt.x+cartPt.y)/2;
    return (tempPt);
}

function isometricToCartesian(isoPt){
    var tempPt=new Phaser.Point();
    tempPt.x=(2*isoPt.y+isoPt.x)/2;
    tempPt.y=(2*isoPt.y-isoPt.x)/2;
    return (tempPt);
}

function getTileCoordinates(cartPt, tileHeight){
    var tempPt=new Phaser.Point();
    tempPt.x=Math.floor(cartPt.x/tileHeight);
    tempPt.y=Math.floor(cartPt.y/tileHeight);
    return(tempPt);
}
