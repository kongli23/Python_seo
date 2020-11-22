function encode_unicode_param(t) {
    for (var e = "", a = 0; a < t.length; a++) {
        var i = t.charCodeAt(a).toString(16);
        2 == i.length ? e += "n" + i : e += i
    }
    return e
}