const config = {
    type: Phaser.AUTO,
    width: 1600,
    height: 800,
    backgroundColor: '#1c2b31',
    //backgroundColor: '#244d1b',
    //parent: 'phaser-example',
    physics: {
        default: 'arcade',
        arcade: {
            gravity: { y: 0 }
        }
    },
    /*plugins: {
        global: [
            { key: 'DialogModalPlugin', plugin: DialogModalPlugin, start: true }
        ]
    },*/
    scene: {
        preload: preload,
        create: create,
        update: update
    }
};

/**************** global variables ************************/
let game = new Phaser.Game(config);
let dX=0,dY=0;
let heroMapPos;
let heroSpeed=2;
let facing='south';//direction the character faces
let layer,mapwidth,mapheight;
//let heroWidth=128;
let player;
let heroMapTile;
let skeletons = {};
let tileWidthHalf;
let scene;
let tilesets;
let centerX,centerY;
//let first=true;
let gameOver=false;
/**************** global variables ************************/



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


let base_path='/static/main/';

function preload ()
{

    //this.load.image('sky', base_path+'assets/sky.png');

    this.load.json('map', base_path+'assets/isometric-grass-and-water.json');
    this.load.spritesheet('tiles', base_path+'assets/isometric-grass-and-water.png', { frameWidth: 64, frameHeight: 64 });
    this.load.spritesheet('skeleton', base_path+'assets/skeleton.png', { frameWidth: 128, frameHeight: 128 });
    this.load.image('house', base_path+'assets/rem_0002.png');
    this.load.image('background', base_path+'assets/background-2.jpg');
    this.load.spritesheet('helicopter',
        base_path+'assets/helicopter-spritesheet.png',
        { frameWidth: 423, frameHeight: 150 }
    );

    this.load.scenePlugin('DialogModalPlugin', base_path+'js/dialog_plugin.js','dialogModalPlugin','dialogModal');
}


let userid='zypang';

class Skeleton extends Phaser.GameObjects.Sprite {
    constructor(scene, x, y){
        super(scene, x, y-16, 'skeleton', 224);

        this.x = x;
        this.y = y;

        this.depth = y + 64;
    }
}

let dialog;
let helicopter;
let mapGroup;
let houseGroup;
let jumpSkeleton;

function create ()
{
    scene = this;

    createAnims();

    //add background
    this.add.image(800,400,'background');

    /**************** create objects for parachuting **********************/
    helicopter=this.physics.add.sprite(0,100,'helicopter',0);
    helicopter.depth=1200;
    helicopter.setVelocityX(200);
    jumpSkeleton = this.physics.add.sprite(800,150,'skeleton',224);
    jumpSkeleton.depth=1500;
    jumpSkeleton.setVisible(false);
    /**************** create objects for parachuting **********************/

    /**************** create dialog modal to show message **********************/
    dialog=this.dialogModal;
    dialog.init();
    dialog.toggleWindow();
    /**************** create dialog modal to show message **********************/


    /**************** create cursor key for movement **********************/
    cursors = this.input.keyboard.createCursorKeys();
    /**************** create cursor key for movement **********************/

    /**************** create group for convenience **********************/
    mapGroup=this.add.group();
    houseGroup=this.add.group();
    /**************** create group for convenience **********************/


    /**************** build map and house **********************/
    buildMap();
    placeHouses();
    /**************** build map and house **********************/

    mapGroup.toggleVisible();
    houseGroup.toggleVisible();

    /**************** put player **********************/
    requestAndRefreshPlayerInfo();
    /**************** put player **********************/

    this.cameras.main.setSize(1600, 800);

    /*this.input.on('pointerdown',function (pointer) {
        console.log(pointer.x,pointer.y);
        skeletons[0].setDestination(pointer.x,pointer.y)
    },this);*/

    // this.cameras.main.scrollX = 800;
}


function createAnims()
{
    /*still:{offset:224,x:0,y:0,opposite:'still'},
    west: { offset: 0, x: -2, y: 0, opposite: 'east' },
    northWest: { offset: 32, x: -2, y: -1, opposite: 'southEast' },
    north: { offset: 64, x: 0, y: -2, opposite: 'south' },
    northEast: { offset: 96, x: 2, y: -1, opposite: 'southWest' },
    east: { offset: 128, x: 2, y: 0, opposite: 'west' },
    southEast: { offset: 160, x: 2, y: 1, opposite: 'northWest' },
    south: { offset: 192, x: 0, y: 2, opposite: 'north' },
    southWest: { offset: 224, x: -2, y: 1, opposite: 'northEast' }*/

    scene.anims.create({
        key: 'heli-fly',
        frames: scene.anims.generateFrameNumbers('helicopter', { start: 0, end: 3 }),
        frameRate:20
    });

    scene.anims.create({
        key: 'idle',
        frames: scene.anims.generateFrameNumbers('skeleton', { start: 224, end: 227 }),
        frameRate:10
    });

    scene.anims.create({
        key: 'west',
        frames: scene.anims.generateFrameNumbers('skeleton', { start: 4, end: 11 }),
        frameRate:10
    });

    scene.anims.create({
        key: 'northwest',
        frames: scene.anims.generateFrameNumbers('skeleton', { start: 36, end: 43 }),
        frameRate:10
    });

    scene.anims.create({
        key: 'north',
        frames: scene.anims.generateFrameNumbers('skeleton', { start: 68, end: 75 }),
        frameRate:10
    });

    scene.anims.create({
        key: 'northeast',
        frames: scene.anims.generateFrameNumbers('skeleton', { start: 100, end: 107 }),
        frameRate:10
    });

    scene.anims.create({
        key: 'east',
        frames: scene.anims.generateFrameNumbers('skeleton', { start: 132, end: 139 }),
        frameRate:10
    });

    scene.anims.create({
        key: 'southeast',
        frames: scene.anims.generateFrameNumbers('skeleton', { start: 164, end: 171 }),
        frameRate:10
    });
    scene.anims.create({
        key: 'south',
        frames: scene.anims.generateFrameNumbers('skeleton', { start: 196, end: 203 }),
        frameRate:10
    });
    scene.anims.create({
        key: 'southwest',
        frames: scene.anims.generateFrameNumbers('skeleton', { start: 228, end: 235 }),
        frameRate:10
    });

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

/****************** auxiliary function to get map tile property*********************/
Array.prototype.containsArray = function(val) {
    let hash = {};
    for(let i=0; i<this.length; i++) {
        hash[this[i]] = i;
    }
    return hash.hasOwnProperty(val);
};
function checkProperty(name)
{
    return function (prpty) {
        return prpty.name===name;
    }
}
function getProperty(tile,name) {
    return tile.properties.find(checkProperty(name)).value;
}
/****************** auxiliary function to get map tile property*********************/

function drawTileIso(x,y,tileId)
{
    /*********function to draw map tile on the scene*************/

    let cartPt=new Phaser.Geom.Point();//This is here for better code readability.
    cartPt.x=x*tileWidthHalf;
    cartPt.y=y*tileWidthHalf;
    let isoPt=cartesianToIsometric(cartPt);
    //let tx = (x - y) * tileWidthHalf;
    //let ty = (x + y) * tileHeightHalf;
    let tx=isoPt.x;
    let ty=isoPt.y;
    let tile = scene.add.image(tx, ty, 'tiles', tileId);
    tile.depth = centerY + ty;
    mapGroup.add(tile);
}

function buildMap ()
{
    //  Parse the data out of the map
    const data = scene.cache.json.get('map');

    tileWidthHalf = data.tilewidth / 2;
    //tileHeightHalf = data.tileheight / 2;

    layer = data.layers[0].data;
    tilesets= data.tilesets[0].tiles;

    mapwidth = data.layers[0].width; //tile count
    mapheight = data.layers[0].height;//tile count

    centerX = mapwidth * tileWidthHalf; //pixel
    centerY = 20; //pixel

    let i = 0;

    for (let y = 0; y < mapheight; y++)
    {
        for (let x = 0; x < mapwidth; x++)
        {
            drawTileIso(x,y,layer[i]-1);
            i++;
        }
    }
}

/********************* place house related ******************************/
let HouseCoords=[[3,21],[21,3]];
let HouseCollidesCoords={};
let houseAuxArrayX= [ 0,1,2,3 ];
let houseAuxArrayY= [ 1,2,3 ];
let houseNames=['good','bad'];
let Houses={};
function placeHouses ()
{
    let len=HouseCoords.length;
    for(let i=0;i<len;++i) {
        let point=HouseCoords[i];
        console.log(point);
        HouseCollidesCoords[houseNames[i]]=[];
        for(let j=0;j<houseAuxArrayX.length;++j)
        {
            for(let k=0;k<houseAuxArrayY.length;++k)
            {
                HouseCollidesCoords[houseNames[i]].push([point[0]+houseAuxArrayX[j],point[1]+houseAuxArrayY[k]]);
            }
        }
        let tmpPos = getCenterXYFromTileCoord(point[0],point[1]);
        //let house = scene.physics.add.staticImage(tmpPos.x,tmpPos.y, 'house');
        let house = scene.add.image(tmpPos.x, tmpPos.y, 'house');
        house.depth = house.y + 118;
        houseGroup.add(house);
        Houses[houseNames[i]]=house;
    }
    console.log(HouseCollidesCoords);
}
/********************* place house related ******************************/

/******************** auxiliary function for parachuting ****************/
function jump() {
    jumpSkeleton.setVisible(true);
    jumpSkeleton.setGravityY(150);
    scene.time.delayedCall(1000,heliFlyOut,[],scene);
    scene.time.delayedCall(15000,heliDestroy,[],scene);
}
function heliDestroy() {
    helicopter.destroy();
    console.log('heli destroy');
}
function heliFlyOut() {
    helicopter.setVelocityX(100);
    mapGroup.toggleVisible();
    houseGroup.toggleVisible();
    //dialog.toggleWindow();
    //dialog.setText('hello world ljdlshflsdl');
}
/******************** auxiliary function for parachuting ****************/

function update ()
{
    /***************** parachuting animation ********************/
    if(helicopter.anims)
        helicopter.anims.play('heli-fly',true);
    if(Math.round(helicopter.x)===800) {
        helicopter.setVelocityX(0);
        scene.time.delayedCall(1000,jump,[],scene);
    }
    if(jumpSkeleton && jumpSkeleton.y>500)
    {
        jumpSkeleton.destroy();
        for(let plyer in skeletons)
        {
            skeletons[plyer].setVisible(true);
        }
    }
    /***************** parachuting animation ********************/

    houseGroup.children.iterate(function (child) {
        child.clearTint();
    });

    /***************** hero move ********************/
    detectKeyInput();
    //if no key is pressed then stop else play walking animation
    if (dY === 0 && dX === 0)
    {
        player.anims.stop();
        player.anims.setCurrentFrame(player.anims.currentAnim.frames[0]);
    }else{
        player.anims.play(facing,true);
    }

    //check if we are walking into an object else move hero in 2D
    if (isWalkableSimple())
    {
        heroMapPos.x +=  heroSpeed * dX;
        heroMapPos.y +=  heroSpeed * dY;
        let heroIsoPos= cartesianToIsometric(heroMapPos);
        //console.log(heroIsoPos);
        //console.log(heroMapPos);
        player.x=heroIsoPos.x;
        player.y=heroIsoPos.y-16;

        //depth correct
        player.depth=heroIsoPos.y+64;

        //get the new hero map tile
        heroMapTile=getTileCoordinates(heroMapPos,tileWidthHalf);
    }
    /***************** hero move ********************/
}



function isWalkableSimple() {
    //let heroCoordinate=getTileCoordinates(heroMapPos,tileWidthHalf);
    let tdX=dX,tdY=dY;
    if(tdX===0.5)
        tdX=1;
    else if(tdX===-0.5)
        tdX=-1;
    if(tdY===0.5)
        tdY=1;
    else if(tdY===-0.5)
        tdY=-1;
    let nextX=heroMapTile.x+tdX+1;
    let nextY=heroMapTile.y+tdY+1;

    if(nextX<0 || nextY<0 || nextX>=mapwidth || nextY>=mapheight) {
        console.log(nextX,nextY);
        return false;
    }
    for(let plyer in playerCollides) {
        if (playerCollides[plyer].containsArray([nextX, nextY])) {
            console.log(nextX, nextY,plyer);
            skeletons[plyer].setTint(0xff0000);
            return false;
        }
    }
    for(let house in HouseCollidesCoords) {
        if (HouseCollidesCoords[house].containsArray([nextX, nextY])) {
            Houses[house].setTint(0x00ff00);

            console.log(nextX, nextY);
            return false;
        }
    }
    let id=layer[nextY*mapheight+nextX]-1;
    //if(layer[newTileCorner1.y*mapheight+newTileCorner1.x==1){
    if(getProperty(tilesets[id],'collides')===true){
        console.log(nextX,nextY);
        return false;
    }
    return true;

}
function detectKeyInput(){//assign direction for character & set x,y speed components
    if (cursors.up.isDown)
    {
        dY = -1;
    }
    else if (cursors.down.isDown)
    {
        dY = 1;
    }
    else
    {
        dY = 0;
    }
    if (cursors.right.isDown)
    {
        dX = 1;
        if (dY === 0)
        {
            facing = "southeast";
        }
        else if (dY===1)
        {
            facing = "south";
            dX = dY=0.5;
        }
        else
        {
            facing = "east";
            dX=0.5;
            dY=-0.5;
        }
    }
    else if (cursors.left.isDown)
    {
        dX = -1;
        if (dY === 0)
        {
            facing = "northwest";
        }
        else if (dY===1)
        {
            facing = "west";
            dY=0.5;
            dX=-0.5;
        }
        else
        {
            facing = "north";
            dX = dY=-0.5;
        }
    }
    else
    {
        dX = 0;
        if (dY === 0)
        {
            //facing="west";
        }
        else if (dY===1)
        {
            facing = "southwest";
        }
        else
        {
            facing = "northeast";
        }
    }
}

/******************** auxiliary function to deal with isometric projection *********************/
function getCartesianFromTileCoordinates(tilePt, tileHeight){
    let tempPt=new Phaser.Geom.Point();
    tempPt.x=tilePt.x*tileHeight;
    tempPt.y=tilePt.y*tileHeight;
    return(tempPt);
}
function cartesianToIsometric(cartPt){
    let tempPt=new Phaser.Geom.Point();
    tempPt.x=centerX+cartPt.x-cartPt.y;
    tempPt.y=centerY+(cartPt.x+cartPt.y)/2;
    return (tempPt);
}

function isometricToCartesian(isoPt){
    let tempPt=new Phaser.Geom.Point();
    tempPt.x=(2*isoPt.y+isoPt.x)/2;
    tempPt.y=(2*isoPt.y-isoPt.x)/2;
    return (tempPt);
}

function getTileCoordinates(cartPt, tileHeight){
    let tempPt=new Phaser.Geom.Point();
    tempPt.x=Math.floor(cartPt.x/tileHeight);
    tempPt.y=Math.floor(cartPt.y/tileHeight);
    return(tempPt);
}
function getCenterXYFromTileCoord(tx,ty) {
    return cartesianToIsometric(getCartesianFromTileCoordinates(new Phaser.Geom.Point(tx,ty),tileWidthHalf));
}
/******************** auxiliary function to deal with isometric projection *********************/

/******************** player related functions *********************/
function requestAndRefreshPlayerInfo() {
    // Add current player
    heroMapTile=new Phaser.Geom.Point(3,15);
    heroMapPos=getCartesianFromTileCoordinates(heroMapTile,tileWidthHalf);

    let heroIsoPos=cartesianToIsometric(heroMapPos);
    skeletons[userid]=scene.add.existing(new Skeleton(scene, heroIsoPos.x, heroIsoPos.y));
    player=skeletons[userid];

    let playerInfos={
        p1:{
            position:[2,5]
        },
        p2:{
            position: [9,21]
        }
    };
    addOtherPlayers(playerInfos);

    for(let plyer in skeletons)
    {
        skeletons[plyer].setVisible(false);
    }
}

function addOtherPlayers(playerInfos) {
    for(plyerId in playerInfos)
    {
        let plyerCoord=playerInfos[plyerId].position;
        let playerIsoPos=cartesianToIsometric(getCartesianFromTileCoordinates(new Phaser.Geom.Point(plyerCoord[0],plyerCoord[1]),tileWidthHalf));

        skeletons[plyerId]=scene.add.existing(new Skeleton(scene, playerIsoPos.x, playerIsoPos.y));
    }
    refreshOtherPlayers(playerInfos);

}
let playerCollides={};
let playerAuxArrayX= [ 0,1 ];
let playerAuxArrayY= [ 0,1 ];

function refreshOtherPlayers(playerInfos) {
    for(plyerId in playerInfos)
    {
        let plyerCoord=playerInfos[plyerId].position;
        let playerIsoPos=cartesianToIsometric(getCartesianFromTileCoordinates(new Phaser.Geom.Point(plyerCoord[0],plyerCoord[1]),tileWidthHalf));

        skeletons[plyerId].x=playerIsoPos.x;
        skeletons[plyerId].y=playerIsoPos.y-16;

        for (let j = 0; j < playerAuxArrayX.length; ++j) {
            for (let k = 0; k < playerAuxArrayY.length; ++k) {
                playerCollides[plyerId]=[];
                playerCollides[plyerId].push([plyerCoord[0] + playerAuxArrayX[j], plyerCoord[1] + playerAuxArrayY[k]]);
            }
        }

        player.anims.play('idle',true);
    }
}
/******************** player related functions *********************/
