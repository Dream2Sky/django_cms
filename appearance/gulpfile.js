var gulp = require("gulp");
var cssnano = require("gulp-cssnano");
var rename = require("gulp-rename");
var uglify = require("gulp-uglify");
var sass = require("gulp-sass");
var browser = require("browser-sync").create();


var path = {
    "html": "templates/**/",
    "css": "./src/css/**/",
    "js": "./src/js/",
    "css_dist": "./dist/css/",
    "js_dist": "./dist/js/"
}

gulp.task("browser_init", (done) => {
    browser.init({
        "server": {
            "baseDir": "./"
        }
    })
})


gulp.task("css", (done) => {
    gulp.src(path.css + "*.scss")
        .pipe(sass().on("error", sass.logError))
        .pipe(cssnano())
        .pipe(rename({
            "suffix": ".min"
        }))
        .pipe(gulp.dest(path.css_dist))
        .pipe(browser.stream())
    done();
});


gulp.task("js", (done) => {
    gulp.src(path.js + "*.js")
        .pipe(uglify())
        .pipe(rename({
            "suffix": ".min"
        }))
        .pipe(gulp.dest(path.js_dist))
        .pipe(browser.stream())
    done();
})


gulp.task("html", (done) => {
    gulp.src(path.html + "*.html")
        .pipe(browser.stream())
    done();
})

gulp.task("watch", (done) => {
    gulp.watch(path.css + "*.scss", gulp.series("css"));
    gulp.watch(path.js + "*.js", gulp.series("js"));
    gulp.watch(path.html + "*.html", gulp.series("html"));
    done();
})

gulp.task("default", gulp.parallel("watch"))