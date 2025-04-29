"""


Task -> Preset -> UI
Registery:
    TaskRegistry
    TaskUIRegistry

"""

import hiero.core
import hiero.ui


from hiero.exporters import FnExternalRenderUI, FnExternalRender


def custom_export_task(task):
    print(f"Custom export task {task}")
    from pprint import pprint as pp

    pp(dir(task))
    pp(vars(task))


class WriteAndSubmitTask(FnExternalRender.NukeRenderTask):
    def __init__(self, structure):
        super().__init__(structure)

    def operation(self):
        """Find the generated nuke script. Submit the script to the farm."""
        # Get the root path of the preset.
        print(self.resolvePath(self._exportPath))

    def startTask(self):
        super().startTask()
        self.operation()


class CleanTask(hiero.core.TaskBase):
    def __init__(self, structure):
        super().__init__(structure)

    def startTask(self):
        super().startTask()
        print("Clean task")


class CustomPreset(hiero.core.RenderTaskPreset):
    def __init__(self, name, properties):
        """Initialise presets to default values"""
        super().__init__(CleanTask, "Something", properties)

        if "writeNodeName" not in self.properties():
            self.properties()["writeNodeName"] = "Write_{ext}"

        self.properties()["burninDataEnabled"] = False

        self._properties["create_directories"] = True

        self._properties.update(properties)

    def supportedItems(self):
        return hiero.core.TaskPresetBase.kAllItems

    def addCustomResolveEntries(self, resolver):
        """addCustomResolveEntries(self, resolver)
        RenderTaskPreset adds specialized tokens specific to this type of export, such as {ext} which returns the output format extension.

        @param resolver: ResolveTable object"""
        # resolver.addResolver("{height}", "Height component of output format", lambda keyword, task: self.height())
        # resolver.addResolver("{width}", "Width component of output format", lambda keyword, task: self.width())
        # resolver.addResolver("{pixelaspect}", "Pixel Aspect of output format", lambda keyword, task: self.pixelAspect())
        resolver.addResolver("{ext}", "Extension of the file to be output", lambda keyword, task: self.extension())


class FreshPreset(hiero.core.RenderTaskPreset):
    def __init__(self, name, properties):
        """Initialise presets to default values"""
        super().__init__(CleanTask, name, properties)

        self.properties().update(properties)

    def addCustomResolveEntries(self, resolver):
        """addCustomResolveEntries(self, resolver)
        RenderTaskPreset adds specialized tokens specific to this type of export, such as {ext} which returns the output format extension.

        @param resolver: ResolveTable object"""
        # resolver.addResolver("{height}", "Height component of output format", lambda keyword, task: self.height())
        # resolver.addResolver("{width}", "Width component of output format", lambda keyword, task: self.width())
        # resolver.addResolver("{pixelaspect}", "Pixel Aspect of output format", lambda keyword, task: self.pixelAspect())
        resolver.addResolver("{ext}", "Extension of the file to be output", lambda keyword, task: self.extension())


class SubmissionPresets(hiero.core.RenderTaskPreset):
    def __init__(self, name, properties):
        """Initialise presets to default values"""
        super().__init__(WriteAndSubmitTask, name, properties)
        self.properties()["burninDataEnabled"] = False
        self.properties()['create_directories'] = True
        self.properties()['writeNodeName'] = 'Write_{ext}'
        self.properties().update(properties)

    def addCustomResolveEntries(self, resolver):
        """addCustomResolveEntries(self, resolver)
        RenderTaskPreset adds specialized tokens specific to this type of export, such as {ext} which returns the output format extension.

        @param resolver: ResolveTable object"""
        # resolver.addResolver("{height}", "Height component of output format", lambda keyword, task: self.height())
        # resolver.addResolver("{width}", "Width component of output format", lambda keyword, task: self.width())
        # resolver.addResolver("{pixelaspect}", "Pixel Aspect of output format", lambda keyword, task: self.pixelAspect())
        resolver.addResolver("{ext}", "Extension of the file to be output", lambda keyword, task: self.extension())


class SubmissionExportInterface(FnExternalRenderUI.NukeRenderTaskUI):
    def __init__(self, preset):
        """Initialize"""
        preset.properties()["burninDataEnabled"] = False
        super().__init__(preset, WriteAndSubmitTask, displayName="Farm Submission 3.0")

        # Copy the Nuke Write submission panel


class BaseExportInterface(hiero.ui.TaskUIBase):
    def __init__(self, preset):
        """Initialize"""
        super().__init__(CleanTask, preset, displayName="Farm Submission 2.0")


print(f"Registering task UI {BaseExportInterface} for {CustomPreset}")
hiero.core.taskRegistry.registerTask(FreshPreset, CleanTask)
hiero.ui.taskUIRegistry.registerTaskUI(FreshPreset, BaseExportInterface)

hiero.core.taskRegistry.registerTask(SubmissionPresets, WriteAndSubmitTask)
hiero.ui.taskUIRegistry.registerTaskUI(SubmissionPresets, SubmissionExportInterface)


# Register the preset with the custom task
# hiero.core.taskRegistry.registerTask(CustomPreset, CleanTask)
# hiero.core.taskRegistry.registerTask(CustomPreset, WriteAndSubmitTask)
# hiero.ui.taskUIRegistry.registerTaskUI(CustomPreset, BaseExportInterface)
