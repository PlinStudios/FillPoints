from krita import *
from .fillpoints_docker import FillPointsDocker

dock_widget_factory = DockWidgetFactory("fillpoints_docker", DockWidgetFactoryBase.DockRight, FillPointsDocker)
Krita.instance().addDockWidgetFactory(dock_widget_factory)
