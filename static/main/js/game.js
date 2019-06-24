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
let heliMoving=true;
let keys;
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
    known_idle:
        {
            startFrame:96,
            endFrame:100,
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
    this.load.image('goodend', base_path+'assets/goodend.png');
    this.load.image('badend', base_path+'assets/badend.png');
    this.load.spritesheet('helicopter',
        base_path+'assets/helicopter-spritesheet.png',
        { frameWidth: 423, frameHeight: 150 }
    );

    this.load.scenePlugin('DialogModalPlugin', base_path+'js/dialog_plugin.js','dialogModalPlugin','dialogModal');
}


let userid;

class Skeleton extends Phaser.GameObjects.Sprite {
    constructor(scene, x, y,user_name,anim_name){
        super(scene, x, y-16, 'skeleton', 224);

        if(anim_name)
            this.anim_name=anim_name;
        else
            this.anim_name='idle';

        this.TEXT_X_OFFSET=0;
        this.TEXT_Y_OFFSET=45;
        this.OBJECT_Y_OFFSET=16;
        this.name_text=scene.add.text(x-this.TEXT_X_OFFSET, y-this.TEXT_Y_OFFSET, user_name, { fontSize: '16px', color: '#ffffff', fontStyle: 'bold'});
        this.name_text.setOrigin(0.5);

        this.user_id=user_name;

        this.x = x;
        this.y = y;

        this.depth = y + 64;
        this.name_text.depth=y+64;
    }
    move(next_x,next_y){
        this.x=next_x;
        this.y=next_y-this.OBJECT_Y_OFFSET;
        this.name_text.x=next_x-this.TEXT_X_OFFSET;
        this.name_text.y=next_y-this.OBJECT_Y_OFFSET-this.TEXT_Y_OFFSET;
        this.depth=next_y+64;
        this.name_text.depth=next_y+64;
    }
    setVisible(visible){
        this.name_text.setVisible(visible);
        super.setVisible(visible);
    }
    setTextTint(tint){
        this.name_text.setTint(tint);
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
    if(parachuting) {
        helicopter = this.physics.add.sprite(0, 100, 'helicopter', 0);
        helicopter.depth = 1200;
        helicopter.setVelocityX(HELI_SPEED);
        heliMoving=true;
        jumpSkeleton = this.physics.add.sprite(800, 150, 'skeleton', 192);
        jumpSkeleton.depth = 1500;
        jumpSkeleton.setVisible(false);
    }
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

    heroMapTile=new Phaser.Geom.Point(0,0);
    /**************** put player **********************/
    //requestAndRefreshPlayerInfo();
    get_init_state();
    /**************** put player **********************/

    keys = this.input.keyboard.addKeys('ESC,SPACE');

    /**************ONLY FOR DEBUG**************************/
    if(!parachuting) {
        setAllVisible(true);
        showMessage('game begin');
    }
    /**************ONLY FOR DEBUG**************************/

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
        frameRate:5
    });
    scene.anims.create({
        key: 'die',
        frames: scene.anims.generateFrameNumbers('skeleton', { start: 212, end: 219 }),
        frameRate:5
    });
    scene.anims.create({
        key: 'known-idle',
        frames: scene.anims.generateFrameNumbers('skeleton', { start: 192, end: 195 }),
        frameRate:5
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
    //tile.depth = centerY + ty;
    tile.depth = 16;
    mapGroup.add(tile);

    //ONLY FOR DEBUG
    /*if(getProperty(tilesets[tileId],'collides')===true) {
        console.log(x,y);
    }*/
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
let HouseCoords=[[3,21],[20,3]];
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
        //console.log(point);
        HouseCollidesCoords[houseNames[i]]=[];
        for(let j=0;j<houseAuxArrayX.length;++j)
        {
            for(let k=0;k<houseAuxArrayY.length;++k)
            {
                HouseCollidesCoords[houseNames[i]].push([point[0]+houseAuxArrayX[j],point[1]+houseAuxArrayY[k]]);
                //console.log(point[0]+houseAuxArrayX[j],point[1]+houseAuxArrayY[k]);
            }
        }
        let tmpPos = getCenterXYFromTileCoord(point[0],point[1]);
        //let house = scene.physics.add.staticImage(tmpPos.x,tmpPos.y, 'house');
        let house = scene.add.image(tmpPos.x, tmpPos.y, 'house');
        house.depth = house.y + 96;
        houseGroup.add(house);
        Houses[houseNames[i]]=house;
    }
    //console.log(HouseCollidesCoords);
}
/********************* place house related ******************************/
function setAllVisible(visible){
    mapGroup.children.iterate(function (child) {
        child.setVisible(visible);
    });
    houseGroup.children.iterate(function (child) {
        child.setVisible(visible);
    });
    for (let plyer in skeletons) {
        skeletons[plyer].setVisible(visible);
    }
    player.setVisible(visible);
}
/******************** auxiliary function for parachuting ****************/
function jump() {
    jumpSkeleton.setVisible(true);
    jumpSkeleton.setGravityY(150);
    mapGroup.toggleVisible();
    houseGroup.toggleVisible();

    scene.time.delayedCall(1000,heliFlyOut,[],scene);
}
function heliDestroy() {
    helicopter.destroy();
    console.log('heli destroy');
}
let HELI_SPEED=200;
function heliFlyOut() {
    helicopter.setVelocityX(HELI_SPEED);
    scene.time.delayedCall(10000,heliDestroy,[],scene);
    //dialog.toggleWindow();
    //dialog.setText('hello world ljdlshflsdl');
}
function showMessage(message,time_out,call_back,anim=true) {
    dialog.setVisible(true);
    dialog.setText(message,anim);
    if(time_out) {
        scene.time.delayedCall(time_out,function () {
            dialog.setVisible(false);
        })
    }
    if(call_back)
        call_back();
}
let waitingKey=true;
let jumped=false;
let parachuting=true;
/******************** auxiliary function for parachuting ****************/
function update ()
{
    if(gameOver)
        return;

    /***************** parachuting animation ********************/
    if (helicopter.anims)
            helicopter.anims.play('heli-fly', true);
    if(parachuting) {
        if (heliMoving) {
            if (Math.round(helicopter.x) >= 800) {
                helicopter.setVelocityX(0);
                heliMoving = false;
            } else
                return;
        }
        if (init_scene)
            return;
        if (!jumped) {
            jumped = true;
            scene.time.delayedCall(1000, jump, [], scene);
        }
        if (jumpSkeleton) {
            jumpSkeleton.play('known-idle',true);
            if (jumpSkeleton.y > 600) {
                jumpSkeleton.destroy();
                for (let plyer in skeletons) {
                    skeletons[plyer].setVisible(true);
                }
                player.setVisible(true);
                parachuting=false;
                showMessage('伞兵模拟作战开始\n你的任务是联系所有的队友，然后选取一个指挥官并在指挥官的' +
                    '领导下寻找遗失在这座岛屿上某座房子内的重要物品\n请使用上下左右键来移动角色\n祝你好运');
                get_cur_state();
            } else
                return;
        }
    }
    /***************** parachuting animation ********************/

    if(init_scene)
        return;
    for(let plyer in skeletons)
    {
        skeletons[plyer].play(skeletons[plyer].anim_name,true);
    }

    if(authenticationState)
    {
        return;
    }
    if(openHouseState)
    {
        if(!waitingKey)
            return;
        if(keys.ESC.isDown)
        {
            dialog.setVisible(false);
            openHouseState=false;
        }
        else if(keys.SPACE.isDown){
            waitingKey=false;
            showMessage('尝试打开这个房子...');
            openHouse(openHouseId);
        }
        return;
    }
    if(choose_commander)
    {
        if(vote_commander)
        {

        }
        return;
    }

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
        player.move(heroIsoPos.x,heroIsoPos.y);
        //player.x=heroIsoPos.x;
        //player.y=heroIsoPos.y-16;

        //depth correct
        //player.depth=heroIsoPos.y+64;

        //get the new hero map tile
        heroMapTile=getTileCoordinates(heroMapPos,tileWidthHalf);
    }
    /***************** hero move ********************/
}


let authenticationState=false;
let openHouseState=false;
let openHouseId;
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
            //skeletons[plyer].setTint(0xff0000);
            if(skeletons[plyer].anim_name === 'idle') {
                showMessage('正在认证' + plyer, undefined, function () {
                    authenticationState = true;
                    processAuthentication(plyer);
                });
            }

            return false;
        }
    }
    for(let house in HouseCollidesCoords) {
        if (HouseCollidesCoords[house].containsArray([nextX, nextY])) {
            Houses[house].setTint(0x00ff00);

            showMessage('你的面前是一个看起来十分华丽的房子，里面貌似有着什么东西在闪闪发光，' +
                '但黑暗处却无法看清，你想打开这座房子吗？\nEsc 取消，Space 打开',undefined,function () {
                openHouseState=true;
                openHouseId=house;
            });

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
    skeletons[userid]=scene.add.existing(new Skeleton(scene, heroIsoPos.x, heroIsoPos.y,userid));
    player=skeletons[userid];
    player.name_text.setColor('#ff0000');

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

        console.log(playerInfos[plyerId].known);
        if(playerInfos[plyerId].known)
        {
            console.log('known');
            skeletons[plyerId]=scene.add.existing(new Skeleton(scene, playerIsoPos.x, playerIsoPos.y,plyerId,'known-idle'));
        }
        else
            skeletons[plyerId]=scene.add.existing(new Skeleton(scene, playerIsoPos.x, playerIsoPos.y,plyerId));
    }
    refreshOtherPlayers(playerInfos);

}
let playerCollides={};
let playerAuxArrayX= [ 0,1 ];
let playerAuxArrayY= [ 0,1 ];

function refreshOtherPlayers(playerInfos) {
    for(plyerId in playerInfos)
    {
        //console.log('plyerId: '+plyerId);
        let plyerCoord=playerInfos[plyerId].position;
        let playerIsoPos=cartesianToIsometric(getCartesianFromTileCoordinates(new Phaser.Geom.Point(plyerCoord[0],plyerCoord[1]),tileWidthHalf));

        skeletons[plyerId].move(playerIsoPos.x,playerIsoPos.y);
        if(playerInfos[plyerId].known)
        {
            skeletons[plyerId].anim_name='known-idle';
        }

        for (let j = 0; j < playerAuxArrayX.length; ++j) {
            for (let k = 0; k < playerAuxArrayY.length; ++k) {
                playerCollides[plyerId]=[];
                playerCollides[plyerId].push([plyerCoord[0] + playerAuxArrayX[j], plyerCoord[1] + playerAuxArrayY[k]]);
            }
        }
    }
}
/******************** player related functions *********************/
let cur_state;
let init_scene=true;
let choose_commander=false;
let vote_commander=false;
let have_commander=false;
function get_init_state() {
    $.ajax({
        method: 'post',
        url: INIT_URL,
        data: {
            user_id:userid,
            position_x:heroMapTile.x,
            position_y:heroMapTile.y,
            csrfmiddlewaretoken: window.CSRF_TOKEN
        }, // serializes the form's elements.
        success: function(data)
        {
            cur_state=JSON.parse(data);
            console.log(cur_state);

            refreshScene(true);

            init_scene=false;
        },
        error:function (data) {
            console.log('ajax error');
            scene.time.delayedCall(1000,function () {
                get_init_state();
            });
        }
    });

}
function get_cur_state(){
    $.ajax({
        method: 'post',
        url: STATE_URL,
        data: {
            user_id:'zypang',
            position_x:heroMapTile.x,
            position_y:heroMapTile.y,
            csrfmiddlewaretoken: window.CSRF_TOKEN
        }, // serializes the form's elements.
        success: function(data)
        {
            cur_state=JSON.parse(data);
            console.log(cur_state);

            refreshScene(false);

            if(cur_state['event'] )
                processEvent(cur_state['event']);

            if(cur_state['can_choose_commander'] && !checkInEvent())
            {
                if(!have_commander) {
                    choose_commander = true;
                    showMessage('所有人已经认证成功，5秒后选取指挥官');
                    scene.time.delayedCall(5000,chooseCommander);
                }
            }

            scene.time.delayedCall(500, function () {
                get_cur_state();
            });
        },
        error:function (data) {
            console.log('ajax error');
            scene.time.delayedCall(1000,function () {
                get_cur_state();
            });
        }
    });

}
function refreshScene(first) {
    if(first)
    {
        userid=cur_state['player'];
        // Add current player
        heroMapTile=new Phaser.Geom.Point(cur_state['position'][0],cur_state['position'][1]);
        heroMapPos=getCartesianFromTileCoordinates(heroMapTile,tileWidthHalf);

        let heroIsoPos=cartesianToIsometric(heroMapPos);
        player=scene.add.existing(new Skeleton(scene, heroIsoPos.x, heroIsoPos.y,userid));
        player.name_text.setColor('#00ff00');
        player.play('idle');

        addOtherPlayers(cur_state['otherPlayers']);
        //console.log('length:'+Object.keys(skeletons).length);

        setAllVisible(false);
    }
    else
    {
        refreshOtherPlayers(cur_state['otherPlayers']);
    }
}
function processEvent(event) {
    if(event.name==='game_over'){
        gameOver=true;
        processGameOver(event.end);
    }
    if(checkInEvent())
        return;
    console.log('process event');
    showMessage(event.info);
    if(event.name==='vote_commander'){
        chooseCommander()
    }
    else if(event.name==='auth'){
    }
    else if(event.name==='open_house'){
        openHouseState=true;
    }
}
function processAuthentication(userBId)
{
    console.log('auth');
    $.ajax({
        method: 'post',
        url: AUTH_URL,
        data: {
            userA_id:userid,
            userB_id:userBId,
            csrfmiddlewaretoken: window.CSRF_TOKEN
        }, // serializes the form's elements.
        success: function(data)
        {
            let auth_result=JSON.parse(data);
            showMessage(auth_result.info);
            if(auth_result.success)
            {
                skeletons[userBId].anim_name='known-idle';
            }
            else
                skeletons[userBId].setTint(0xff0000);

            scene.time.delayedCall(1000,function () {
                authenticationState=false;
            });
        },
        error:function (data) {
            console.log('ajax error');
        }
    });
}
let commander_candidates;
function processVoteCommander(candidates) {
    choose_commander=true;
    vote_commander=true;
    commander_candidates=candidates;
    candidates.forEach(function (user_id) {
        let sprite;
        if(user_id===userid)
            sprite=player;
        else
            sprite=skeletons[user_id];
        sprite.setInteractive();
        //sprite.setTextTint(0x00ff00);
        sprite.on('pointerover', function () {
            sprite.setTint(0xff00ff);
        });

        sprite.on('pointerout', function () {
            sprite.clearTint();
        });
        sprite.on('pointerdown',function () {
            vote_for_commander(sprite.user_id);
        });
    });
}
function chooseCommander()
{
    if(have_commander)
        return;
    console.log('choose commander');
    $.ajax({
        method: 'post',
        url: COMMANDER_URL,
        data: {
            user_id:userid,
            vote:0,
            csrfmiddlewaretoken: window.CSRF_TOKEN
        }, // serializes the form's elements.
        success: function(data)
        {
            let result=JSON.parse(data);
            showMessage(result.info,undefined,undefined,false);
            if(result.success)
            {
                player.clearTint();
                for(let plyer in skeletons)
                {
                    skeletons[plyer].clearTint();
                }
                if(result.commander===userid){
                    player.setTint(0xffd700);
                    player.setTextTint(0xffd700);
                }
                else {
                    skeletons[result.commander].setTint(0xffd700);
                    skeletons[result.commander].setTextTint(0xffd700);
                }
                have_commander=true;

                scene.time.delayedCall(1000,function () {
                    choose_commander=false;
                });
            }
            else
            {
                if(result.need_vote)
                {
                    vote_commander=true;
                    processVoteCommander(result.candidates);
                }
                else
                    scene.time.delayedCall(1000,chooseCommander);
            }
        },
        error:function (data) {
            console.log('ajax error');
        }
    });
}
function vote_for_commander(commanderId)
{
    console.log(commanderId);

    commander_candidates.forEach(function (candidate) {
        if(candidate===userid) {
            player.removeInteractive();
        }
        else
            skeletons[candidate].removeInteractive();
    });
    $.ajax({
        method: 'post',
        url: COMMANDER_URL,
        data: {
            user_id:userid,
            vote:1,
            vote_commander:commanderId,
            csrfmiddlewaretoken: window.CSRF_TOKEN
        }, // serializes the form's elements.
        success: function(data)
        {
            let result=JSON.parse(data);
            showMessage(result.info);
            chooseCommander();
        },
        error:function (data) {
            showMessage('网络连接失败或者服务器错误，1秒后重试');
            scene.time.delayedCall(1000,function(){vote_for_commander(commanderId)});
        }
    });
}
function processGameOver(goodend) {
    gameOver=true;
    scene.time.removeAllEvents();
    //dialog.setVisible(false);
    if(goodend)
    {
        showMessage('很幸运，打开房子之后顺利找到了我军所需的重要物品，任务成功！');
        scene.time.delayedCall(5000,function () {
            dialog.setVisible(false);
            scene.add.image(800,400,'goodend').depth=1500;
        });
    }
    else
    {
        showMessage('打开房子的那一刻，意外的事发生了，房子里是敌军的化学毒气，毒气很快蔓延全岛，所有人不幸遇难，任务失败！');
        scene.time.delayedCall(5000,function () {
            dialog.setVisible(false);
            scene.add.image(800,400,'badend').depth=1500;
            for(let plyer in skeletons)
            {
                skeletons[plyer].play('die',true);
            }
            player.play('die',true);
        });
    }

}
function openHouse(houseName) {
    console.log('opening house '+houseName);
    $.ajax({
        method: 'post',
        url: OPEN_HOUSE_URL,
        data: {
            user_id:userid,
            house_name:houseName,
            csrfmiddlewaretoken: window.CSRF_TOKEN
        }, // serializes the form's elements.
        success: function(data)
        {
            console.log(data);
            //let ending=getRndInteger(0,2);
            let ending=0;
            let result=JSON.parse(data);
            showMessage(result.info);
            waitingKey=true;
            if(result.success)
            {
                gameOver=true;
                $.ajax({
                    method:'post',
                    url: GAME_OVER_URL,
                    data:{
                        user_id:userid,
                        ending:ending,
                        csrfmiddlewaretoken: window.CSRF_TOKEN
                    },
                    success: function (data) {
                        console.log('game over sent');
                    },
                    error: function (data) {
                        console.log('game over ajax error: '+data);
                    }
                });
                scene.time.delayedCall(5000,function(){
                    processGameOver(ending);
                });
            }

            scene.time.delayedCall(1000,function () {
                openHouseState=false;
            });
        },
        error:function (data) {
            console.log('ajax error');
        }
    });
}
function checkInEvent()
{
    return authenticationState || openHouseState || choose_commander || vote_commander || gameOver;
}
function wait(ms){
    let start = new Date().getTime();
    let end = start;
    while(end < start + ms) {
        end = new Date().getTime();
    }
}
function getRndInteger(min, max) {
  return Math.floor(Math.random() * (max - min) ) + min;
}
