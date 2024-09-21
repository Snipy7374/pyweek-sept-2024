from __future__ import annotations

import json
import typing
import collections.abc

import arcade
import arcade.gui
from PIL import Image

import constants

if typing.TYPE_CHECKING:
    from gui.views.main_menu import MainMenuView

ComponentT = typing.TypeVar("ComponentT", bound=arcade.gui.UIWidget)
ComponentCallback = collections.abc.Callable[[arcade.gui.UIEvent], None]

OFF_TEXTURE = Image.new("RGBA", (28, 28), (255, 255, 255, 255))
OFF_TEXTURE.paste((0, 0, 0, 255), (2, 2, 26, 26))


class OptionEntryContainer(arcade.gui.UIBoxLayout, typing.Generic[ComponentT]):
    def __init__(
        self,
        label: str,
        *,
        component: ComponentT,
        component_callback: ComponentCallback,
        event_name: str,
        option_state_label: str | None = None,
    ) -> None:
        super().__init__(align="center", space_between=7)
        self.label = arcade.gui.UILabel(
            text=label,
            font_size=18,
            align="center",
        )
        self.add(self.label)

        self.entry = arcade.gui.UIBoxLayout(vertical=False, space_between=15)

        self.component = component
        self.component.__setattr__(event_name, component_callback)
        self.entry.add(component)

        # for dropdowns we don't provide the state label, instead
        # we set the component default to the state
        if not isinstance(component, arcade.gui.UIDropdown):
            self.option_label = arcade.gui.UILabel(
                text=option_state_label,  # type: ignore
                font_size=14,
            )
            self.entry.add(self.option_label)

        self.add(self.entry)

    @property
    def value(self) -> bool | str | None:
        if isinstance(self.component, arcade.gui.UITextureToggle):
            return self.component.value
        elif isinstance(self.component, arcade.gui.UIDropdown):
            return self.value

    @value.setter
    def value(self, _v: bool | str) -> None:
        if isinstance(self.component, arcade.gui.UITextureToggle):
            self.component.value = _v  # type: ignore
            self.option_label.text = "Enabled" if _v else "Disabled"
        elif isinstance(self.component, arcade.gui.UIDropdown):
            self.component.value = _v  # type: ignore


class OptionsMenu(arcade.gui.UIMouseFilterMixin, arcade.gui.UIAnchorLayout):
    settings: dict[str, typing.Any]

    def __init__(
        self,
        *,
        main_view: MainMenuView,
        parent_manager: arcade.gui.UIManager,
        temp_manager: arcade.gui.UIAnchorLayout,
        backgound_child: arcade.gui.UIWidget,
    ) -> None:
        super().__init__(
            x=parent_manager.window.center_x,
            y=parent_manager.window.center_y,
            size_hint=(0, 0),
        )
        self.main_view = main_view
        self.parent_manager = parent_manager
        self.temp_layout = temp_manager
        self.background_child = backgound_child
        self.setted_up: bool = False

        # Setup frame which will act like the window.
        frame = self.add(
            arcade.gui.UIAnchorLayout(
                width=900,
                height=900,
                size_hint_min=(600, 720),
            )
        )
        frame.with_padding(left=20, right=20, top=60, bottom=80)
        menu_texture = arcade.load_texture(constants.ASSETS_DIR / "menu_texture.png")
        texture = arcade.gui.NinePatchTexture(0, 0, 0, 0, menu_texture)
        frame.with_background(texture=texture)

        button_texture = arcade.load_texture(constants.ASSETS_DIR / "button_texture.png")
        back_button = arcade.gui.UITextureButton(
            text="Back",
            texture=button_texture,
            texture_hovered=button_texture,
            texture_pressed=button_texture,
            size_hint=(0, 0),
            size_hint_min=(320, 75),
            size_hint_max=(350, 100),
        )
        back_button.on_click = self.on_click_back_button  # type: ignore

        title_label = arcade.gui.UILabel(
            text="Options Menu",
            align="center",
            font_name="Alagard",
            font_size=36,
            multiline=False,
        )
        # Adding some extra space around the title.
        title_label_space = arcade.gui.UISpace(
            height=30,
            size_hint=(0, 0),
            size_hint_min=(0, 5),
            size_hint_max=(0, 30),
        )

        on_texture = arcade.load_texture(constants.ASSETS_DIR / "button_texture.png")
        # off_texture = arcade.load_texture(constants.ASSETS_DIR / "solid_black.png")
        off_texture = arcade.Texture(OFF_TEXTURE)

        title_layout = arcade.gui.UIBoxLayout(align="center", space_between=50)
        title_layout.add(title_label_space)
        title_layout.add(title_label)

        back_button_layout = arcade.gui.UIAnchorLayout()
        back_button_layout.add(
            back_button,
            anchor_x="center",
            anchor_y="bottom",
            align_y=40,
        )

        widget_layout = arcade.gui.UIBoxLayout(
            align="center",
            space_between=20,
        )
        graphic_toggles = arcade.gui.UIBoxLayout(vertical=False, space_between=40)
        graphic_toggles2 = arcade.gui.UIBoxLayout(vertical=False, space_between=40)

        vsync_toggle = arcade.gui.UITextureToggle(
            on_texture=on_texture, off_texture=off_texture, width=30, height=30
        )
        self.vsync_toggle = OptionEntryContainer(
            "V-Sync",
            option_state_label="Disabled",
            component=vsync_toggle,
            component_callback=self.vsync_toggle_callback,  # type: ignore
            event_name="on_change",
        )

        antialiasing_toggle = arcade.gui.UITextureToggle(
            on_texture=on_texture, off_texture=off_texture, width=30, height=30
        )
        self.antialiasing_toggle = OptionEntryContainer(
            "Antialiasing",
            option_state_label="Enabled",
            component=antialiasing_toggle,
            component_callback=self.antialiasing_toggle_callback,  # type: ignore
            event_name="on_change",
        )

        fullscreen_toggle = arcade.gui.UITextureToggle(
            on_texture=on_texture, off_texture=off_texture, width=30, height=30
        )
        self.fullscreen_toggle = OptionEntryContainer(
            "Fullscreen",
            option_state_label="Disabled",
            component=fullscreen_toggle,
            component_callback=self.fullscreen_callback,  # type: ignore
            event_name="on_change",
        )

        graphic_toggles.add(self.vsync_toggle)
        graphic_toggles.add(self.antialiasing_toggle)
        graphic_toggles2.add(self.fullscreen_toggle)
        widget_layout.add(graphic_toggles)
        widget_layout.add(graphic_toggles2)

        antialiasing_dropdown = arcade.gui.UIDropdown(
            options=["2x", "4x", "8x", "16x"],
            height=20,
            width=150,
        )
        self.antialiasing_samples_dropdown = OptionEntryContainer(
            "Antialiasing samples",
            component=antialiasing_dropdown,
            component_callback=self.antialiasing_dropdown_callback,  # type: ignore
            event_name="on_change",
        )
        widget_layout.add(self.antialiasing_samples_dropdown)

        window_size_dropdown = arcade.gui.UIDropdown(
            options=[
                "1920x1080",
                "1536x864",
                "1366x768",
            ],
        )
        self.window_size_dropdown = OptionEntryContainer(
            "Screen Resolution",
            component=window_size_dropdown,
            component_callback=self.window_size_dropdown_callback,  # type: ignore
            event_name="on_change",
        )
        widget_layout.add(self.window_size_dropdown)

        frame.add(child=title_layout, anchor_x="center_x", anchor_y="top")
        frame.add(
            child=widget_layout,
            anchor_x="center",
            anchor_y="center",
        )
        frame.add(
            child=back_button_layout,
            anchor_x="center",
            anchor_y="bottom",
        )

    def vsync_toggle_callback(self, event: arcade.gui.UIOnChangeEvent) -> None:
        # this event was triggered by the loading of the current settings
        # skipping it
        if not self.setted_up:
            return

        self.save_setting("vsync_toggle", event.new_value)
        self.parent_manager.window.set_vsync(event.new_value)
        self.vsync_toggle.value = event.new_value

    def antialiasing_toggle_callback(self, event: arcade.gui.UIOnChangeEvent) -> None:
        # this event was triggered by the loading of the current settings
        # skipping it
        if not self.setted_up:
            return

        self.save_setting("antialiasing_toggle", event.new_value)
        self.antialiasing_toggle.value = event.new_value

    def antialiasing_dropdown_callback(self, event: arcade.gui.UIOnChangeEvent) -> None:
        # this event was triggered by the loading of the current settings
        # skipping it
        if not self.setted_up:
            return

        self.save_setting("antialiasing_samples_dropdown", int(event.new_value[:-1]))
        self.antialiasing_samples_dropdown._value = event.new_value  # type: ignore

    def window_size_dropdown_callback(self, event: arcade.gui.UIOnChangeEvent) -> None:
        # this event was triggered by the loading of the current settings
        # skipping it
        if not self.setted_up:
            return

        self.save_setting("window_size_dropdown", event.new_value)
        width, height = map(int, event.new_value.split("x"))

        # skip setting the new window size if we are in fullscreen mode
        # this errors out
        if self.parent_manager.window.fullscreen:
            self.parent_manager.window.set_size(width, height)
            self.main_view.manager.trigger_render()
            self.temp_layout.trigger_full_render()
        self.window_size_dropdown._value = event.new_value  # type: ignore

    def fullscreen_callback(self, event: arcade.gui.UIOnChangeEvent) -> None:
        # this event was triggered by the loading of the current settings
        # skipping it
        if not self.setted_up:
            return

        self.save_setting("fullscreen_toggle", event.new_value)

        # we need to pass the size in case the user disable fullscreen
        # so the window has the correct size
        size = self.settings["window_size_dropdown"]
        if size:
            width, height = map(int, size.split("x"))
        else:
            width, height = arcade.get_display_size()

        self.parent_manager.window.set_fullscreen(
            event.new_value,
            width=width,
            height=height,
        )
        self.fullscreen_toggle.value = event.new_value

        self.main_view.manager.trigger_render()
        self.main_view.ui_layout.trigger_full_render()
        self.temp_layout.trigger_full_render()

    def setup_from_dict(self) -> None:
        self.settings: dict[str, typing.Any] = self.load_saved_settings()

        for key, value in self.settings.copy().items():
            if key.endswith(("_toggle", "_dropdown")):
                attr = self.__getattribute__(key)
                attr.value = value
        self.setted_up = True

    def save_setting(self, setting: str, value: typing.Any) -> None:
        with open(constants.SETTINGS_DIR / "saved_settings.json", "w") as f:
            self.settings[setting] = value
            json.dump(self.settings, f, indent=2)

    def load_saved_settings(self) -> typing.Any:
        with open(constants.SETTINGS_DIR / "saved_settings.json") as f:
            data = json.load(f)
        return data

    def on_click_back_button(self, _: arcade.gui.UIOnClickEvent) -> None:
        # Removes the widget from the manager.
        # After this the manager will respond to its events like it previously did.
        self.parent_manager.remove(self.temp_layout)
        self.parent_manager.remove(self.background_child)

        for btn in self.main_view.box:
            btn.disabled = False  # type: ignore
