/**
 * (c) 2012 GraphBrain Ltd. All rigths reserved.
 */

// Link
var Link = function(id, orig, sorig, targ, starg, label) {
    this.id = id;
    this.orig = orig;
    this.sorig = sorig;
    this.targ = targ;
    this.starg = starg;
    this.label = label;
    this.ox = 0;
    this.oy = 0;
    this.tx = 0;
    this.ty = 0;

    this.len = 0;

    // add common VisualObj capabilities
    makeVisualObj(this);
}

Link.prototype.updatePos = function() {
    var orig = false;
    var targ = false;
    var origSuper = false;
    var targSuper = false;

    if (this.orig) {
        orig = this.orig;
    }
    else if (this.sorig) {
        orig = this.sorig;
        this.origSuper = true;
    }
    
    if (this.targ) {
        targ = this.targ;
    }
    else if (this.starg) {
        targ = this.starg;
        this.targSuper = true;
    }

    var x0 = orig.rpos[0];
    var y0 = orig.rpos[1];
    var x1 = targ.rpos[0];
    var y1 = targ.rpos[1];

    p0 = interRect(x0, y0, x1, y1, orig.x0, orig.y0, orig.x1, orig.y1);
    p1 = interRect(x1, y1, x0, y0, targ.x0, targ.y0, targ.x1, targ.y1);

    this.x0 = p0[0];
    this.y0 = p0[1];
    this.z0 = orig.rpos[2];
    this.x1 = p1[0];
    this.y1 = p1[1];
    this.z1 = targ.rpos[2];

    // calc length
    var dx = this.x1 - this.x0;
    var dy = this.y1 - this.y0;
    this.dx = dx;
    this.dy = dy;
    this.len = (dx * dx) + (dy * dy);
    this.len = Math.sqrt(this.len);

    // calc center
    this.cx = this.x0 + ((this.x1 - this.x0) / 2)
    this.cy = this.y0 + ((this.y1 - this.y0) / 2)

    var slope = (this.y1 - this.y0) / (this.x1 - this.x0);
    this.angle = Math.atan(slope);

    var p = [[0, 0], [0, 0], [0, 0], [0, 0], [0, 0]];

    if ((this.x0 < this.x1) || ((this.x0 == this.x1) && (this.y0 < this.y1))) {
        p[0][0] = -this.halfWidth;     p[0][1] = -this.halfHeight;
        p[1][0] = -this.halfWidth;     p[1][1] = this.halfHeight;
        p[2][0] = this.halfWidth;      p[2][1] = this.halfHeight;
        p[3][0] = this.halfWidth + 6;  p[3][1] = 0;
        p[4][0] = this.halfWidth;      p[4][1] = -this.halfHeight;
    }
    else {
        p[0][0] = -this.halfWidth;     p[0][1] = -this.halfHeight;
        p[1][0] = -this.halfWidth - 6; p[1][1] = 0;
        p[2][0] = -this.halfWidth;     p[2][1] = this.halfHeight;
        p[3][0] = this.halfWidth;      p[3][1] = this.halfHeight;
        p[4][0] = this.halfWidth;      p[4][1] = -this.halfHeight;
    }

    for (i = 0; i < 5; i++) {
        rotateAndTranslate(p[i], this.angle, this.cx, this.cy);
    }

    this.points = p;

    // calc bounding rectangle
    if ((this.x0 < this.x1) || ((this.x0 == this.x1) && (this.y0 < this.y1))) {
        this.rect.v1.x = p[0][0];
        this.rect.v1.y = p[0][1];
        this.rect.v2.x = p[1][0];
        this.rect.v2.y = p[1][1];
        this.rect.v3.x = p[2][0];
        this.rect.v3.y = p[2][1];
        this.rect.v4.x = p[4][0];
        this.rect.v4.y = p[4][1];
    }
    else {
        this.rect.v1.x = p[0][0];
        this.rect.v1.y = p[0][1];
        this.rect.v2.x = p[2][0];
        this.rect.v2.y = p[2][1];
        this.rect.v3.x = p[3][0];
        this.rect.v3.y = p[3][1];
        this.rect.v4.x = p[4][0];
        this.rect.v4.y = p[4][1];   
    }
}

Link.prototype.draw = function() {
    this.updatePos();

    // set link color according to label text
    // TODO: this should be server side 
    var color = '#FFD326';
    var textcolor = '#000'

    if (~this.label.indexOf('direct'))
        color = '#BEE512';
    else if (~this.label.indexOf('char'))
        color = '#DFFD59';
    else if (~this.label.indexOf('play'))
        color = '#FFFC26';
    else if (~this.label.indexOf('is')) {
        color = '#ED9107';
        textcolor = '#FFF'
    }

    // draw line
    context.strokeStyle = color;
    context.fillStyle = color;
    context.lineWidth = 0.7;

    context.beginPath();
    context.moveTo(this.x0, this.y0);
    context.lineTo(this.x1, this.y1);
    context.stroke();

    // draw circles at both ends of line
    if (this.origSuper) {
        context.fillStyle = '#505050';
    }
    else {
        context.fillStyle = color;   
    }
    context.beginPath();
    var radius = 4;
    context.arc(this.x0, this.y0, radius, 0, 2 * Math.PI, false);
    context.fill();
    if (this.targSuper) {
        context.fillStyle = '#505050';
    }
    else {
        context.fillStyle = color;   
    }
    context.beginPath();
    context.arc(this.x1, this.y1, radius, 0, 2 * Math.PI, false);
    context.fill();
    context.fillStyle = color;

    // draw label area
    context.beginPath();
    context.moveTo(this.points[0][0], this.points[0][1]);
    for (i = 1; i < 5; i++) {
        context.lineTo(this.points[i][0], this.points[i][1]);
    }
    
    context.closePath();
    context.fill();

    // draw label text
    context.save();
    context.translate(this.cx, this.cy);
    context.rotate(this.angle);
    context.font = "10pt Sans-Serif";
    context.fillStyle = textcolor;
    context.textAlign = "center";
    context.textBaseline = "middle";
    context.fillText(this.label, 0, 0);
    context.restore();
}

Link.prototype.pointInLabel = function(p) {
    return (pointInTriangle(this.points[0], this.points[1], this.points[2], p)
        || pointInTriangle(this.points[2], this.points[3], this.points[4], p)
        || pointInTriangle(this.points[0], this.points[2], this.points[4], p));
}

Link.prototype.intersectsLink = function(link2) {
    return lineSegsOverlap(this.x0, this.y0, this.x1, this.y1, link2.x0, link2.y0, link2.x1, link2.y1);
}

Link.prototype.intersectsSNode = function(snode) {
    return lineRectOverlap(this.x0, this.y0, this.x1, this.y1, snode.rect);
}

Link.prototype.place = function() {
    // create link div
    var linkDiv = document.createElement('div');
    linkDiv.setAttribute('class', 'link');
    linkDiv.setAttribute('id', 'link' + this.id);
    
    var nodesDiv = document.getElementById("nodesDiv");
    nodesDiv.appendChild(linkDiv);

    $('#link' + this.id).append('<div class="linkLine" id="linkLine' + this.id + '"></div>');
    $('#link' + this.id).append('<div class="linkLabel" id="linkLabel' + this.id + '">' + this.label + '</div>');

    var height = $('#link' + this.id).outerHeight();
    this.halfHeight = height / 2;
    var labelWidth = $('#linkLabel' + this.id).outerWidth();
    this.halfLabelWidth = labelWidth / 2;

    $('#linkLine' + this.id).css('top', '' + this.halfHeight + 'px');
}

Link.prototype.visualUpdate = function() {
    var deltaX = this.x1 - this.x0;
    var deltaY = this.y1 - this.y0;
    var deltaZ = this.z1 - this.z0;
    
    var cx = this.x0 + (deltaX / 2);
    var cy = this.y0 + (deltaY / 2);
    var cz = this.z0 + (deltaZ / 2);

    var len = Math.sqrt((deltaX * deltaX) + (deltaY * deltaY) + (deltaZ * deltaZ));

    var rotz = Math.atan2(deltaY, deltaX);
    var roty;
    if (deltaX >= 0) {
        roty = -Math.atan2(deltaZ * Math.cos(rotz), deltaX);
    }
    else {
        roty = Math.atan2(deltaZ * Math.cos(rotz), -deltaX);
    }

    $('#link' + this.id).css('width', '' + len + 'px');
    $('#linkLine' + this.id).css('height', '1px');
    $('#linkLabel' + this.id).css('left', '' + ((len / 2) - this.halfLabelWidth) + 'px');

    // apply translation
    var tx = cx - (len / 2);
    var ty = cy - this.halfHeight;
    var tz = cz;
    
    var transformStr = 'translate3d(' + tx + 'px,' + ty + 'px,' + tz + 'px)'
        + ' rotateZ(' + rotz + 'rad)'
        + ' rotateY(' + roty + 'rad)';
    $('#link' + this.id).css('-webkit-transform', transformStr);
}