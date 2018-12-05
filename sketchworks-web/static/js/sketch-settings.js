function SketchSettings(settings, name) {
    var self = this;
    self.name = name || settings.filePath;
    self.filePath = ko.observable(settings.filePath);
    self.scale = ko.observable(settings.scale);
    self.xOffset = ko.observable(settings.xOffset);
    self.yOffset = ko.observable(settings.yOffset);
    self.estimate = ko.observable();

    self.toDict = function() {
        return {
            name: self.name,
            filePath: self.filePath(),
            scale: self.scale(),
            xOffset: self.xOffset(),
            yOffset: self.yOffset(),
            estimate: self.estimate()
        }
    }
}
