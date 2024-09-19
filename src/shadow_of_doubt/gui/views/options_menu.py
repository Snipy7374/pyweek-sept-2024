import json

import typing
import collections.abc

import arcade
import arcade.gui

from shadow_of_doubt import constants

ComponentT = typing.TypeVar("ComponentT", bound=arcade.gui.UIWidget)
ComponentCallback = collections.abc.Callable[[arcade.gui.UIEvent], None]


class OptionEntryContainer(arcade.gui.UIBoxLayout, typing.Generic[ComponentT]):
    def __init__(
        self,
        label: str,
        *,
        option_state_label: str,
        component: ComponentT,
        component_callback: ComponentCallback,
        event_name: str,
    ) -> None:
        super().__init__(align="center", space_between=7)
        self.label = arcade.gui.UILabel(
            text=label,
            font_size=18,
            align="center",
        )
        self.add(self.label)

        self.entry = arcade.gui.UIBoxLayout(vertical=False, space_between=15)
        self.option_label = arcade.gui.UILabel(
            text=option_state_label,
            font_size=14,
        )

        self.component = component
        self.component.__setattr__(event_name, component_callback)
        self.entry.add(component)
        self.entry.add(self.option_label)
        self.add(self.entry)

    @property
    def value(self) -> bool | str | None:
        if isinstance(self.component, arcade.gui.UITextureToggle):
            return self.component.value
        elif isinstance(self.component, arcade.gui.UIDropdown):
            return self.option_label.text

    @value.setter
    def value(self, _v: bool | str) -> None:
        if isinstance(self.component, arcade.gui.UITextureToggle):
            self.component.value = _v  # type: ignore
            self.option_label.text = "Enabled" if _v else "Disabled"
        elif isinstance(self.component, arcade.gui.UIDropdown):
            self.option_label.text = _v


class OptionsMenu(arcade.gui.UIMouseFilterMixin, arcade.gui.UIAnchorLayout):
    settings: dict[str, typing.Any]

    def __init__(
        self,
        parent_manager: arcade.gui.UIManager,
        backgound_child: arcade.gui.UIWidget,
    ) -> None:
        super().__init__(
            x=parent_manager.window.center_x,
            y=parent_manager.window.center_y,
            size_hint=(0, 0),
        )
        self.parent_manager = parent_manager
        self.background_child = backgound_child

        # Setup frame which will act like the window.
        frame = self.add(
            arcade.gui.UIAnchorLayout(
                width=800,
                height=700,
                size_hint=(0, 0),
                size_hint_min=(600, 500),
                size_hint_max=(800, 700),
            )
        )
        frame.with_padding(all=20)
        button_texture = arcade.load_texture(constants.ASSETS_DIR / "button_texture.png")
        texture = arcade.gui.NinePatchTexture(0, 0, 0, 0, button_texture)
        frame.with_background(texture=texture)

        back_button = arcade.gui.UIFlatButton(text="Back", width=250)
        back_button.on_click = self.on_click_back_button  # type: ignore

        title_label = arcade.gui.UILabel(
            text="Options Menu",
            align="center",
            font_name="DungeonFont",
            font_size=32,
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
        off_texture = arcade.load_texture(constants.ASSETS_DIR / "solid_black.png")

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
            align="left",
            space_between=20,
        )
        graphic_toggles = arcade.gui.UIBoxLayout(vertical=False, space_between=40)

        vsync_toggle = arcade.gui.UITextureToggle(
            on_texture=on_texture, off_texture=off_texture, width=30, height=30
        )
        self.vsync_toggle = OptionEntryContainer(
            "V-Sync",
            option_state_label="Disabled",
            component=vsync_toggle,
            component_callback=self.vsync_toggle_callback,
            event_name="on_change",
        )

        antialiasing_toggle = arcade.gui.UITextureToggle(
            on_texture=on_texture, off_texture=off_texture, width=30, height=30
        )
        self.antialiasing_toggle = OptionEntryContainer(
            "Antialiasing",
            option_state_label="Enabled",
            component=antialiasing_toggle,
            component_callback=self.antialiasing_toggle_callback,
            event_name="on_change",
        )
        graphic_toggles.add(self.vsync_toggle)
        graphic_toggles.add(self.antialiasing_toggle)
        widget_layout.add(graphic_toggles)

        antialiasing_dropdown = arcade.gui.UIDropdown(
            default="4x",
            options=["2x", "4x", "8x", "16x"],
            height=20,
            width=150,
        )
        self.antialiasing_samples_dropdown = OptionEntryContainer(
            "Antialiasing samples",
            option_state_label="4x",
            component=antialiasing_dropdown,
            component_callback=self.antialiasing_dropdown_callback,
            event_name="on_change",
        )
        widget_layout.add(self.antialiasing_samples_dropdown)

        window_size_dropdown = arcade.gui.UIDropdown(
            default="1920x1080", options=["1920x1080", "1536x864", "1366x768"]
        )
        self.window_size_dropdown = OptionEntryContainer(
            "Screen Resolution",
            option_state_label="1920x1080",
            component=window_size_dropdown,
            component_callback=self.window_size_dropdown_callback,
            event_name="on_change",
        )
        widget_layout.add(self.window_size_dropdown)

        frame.add(child=title_layout, anchor_x="center_x", anchor_y="top")
        frame.add(
            child=widget_layout,
            anchor_x="left",
            anchor_y="center",
            align_x=125,
        )
        frame.add(
            child=back_button_layout,
            anchor_x="center",
            anchor_y="bottom",
        )

    def vsync_toggle_callback(self, event: arcade.gui.UIOnChangeEvent) -> None:
        self.save_setting("vsync_toggle", event.new_value)
        self.vsync_toggle.value = event.new_value

    def antialiasing_toggle_callback(self, event: arcade.gui.UIOnChangeEvent) -> None:
        self.save_setting("antialiasing_toggle", event.new_value)
        self.antialiasing_toggle.value = event.new_value

    def antialiasing_dropdown_callback(self, event: arcade.gui.UIOnChangeEvent) -> None:
        self.save_setting("antialiasing_samples", int(event.new_value[: len(event.new_value) - 1]))
        self.antialiasing_samples_dropdown.option_label.text = event.new_value

    def window_size_dropdown_callback(self, event: arcade.gui.UIOnChangeEvent) -> None:
        self.save_setting("window_size", event.new_value)
        self.window_size_dropdown.option_label.text = event.new_value

    def setup_from_dict(self) -> None:
        self.settings: dict[str, typing.Any] = self.load_saved_settings()

        for key, value in self.settings.copy().items():
            if key.endswith(("_toggle", "_dropdown")):
                attr = self.__getattribute__(key)
                attr.value = value

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
        self.parent_manager.remove(self)
        self.parent_manager.remove(self.background_child)
