import json

import typing

import arcade
import arcade.gui

from shadow_of_doubt import constants


class OptionEntryContainer(arcade.gui.UIBoxLayout):
    def __init__(
        self,
        label: str,
        *,
        option_state_label: str,
        component: arcade.gui.UIWidget,
        value: bool = False,
    ) -> None:
        super().__init__(align="left", space_between=5)
        self.label = arcade.gui.UILabel(
            text=label,
            font_size=18,
        )
        self.add(self.label)

        self.entry = arcade.gui.UIBoxLayout(vertical=False, space_between=10)
        self.option_label = arcade.gui.UILabel(
            text=option_state_label,
            font_size=14,
        )

        self._value = value
        self.component = component
        self.entry.add(component)
        self.entry.add(self.option_label)
        self.add(self.entry)

    @property
    def value(self) -> bool | None:
        if not isinstance(self.component, arcade.gui.UITextureToggle):
            return
        return self.component.value

    @value.setter
    def value(self, _v: bool) -> None:
        if not isinstance(self.component, arcade.gui.UITextureToggle):
            return
        self.component.value = _v
        self.option_label.text = "Enabled" if _v else "Disabled"


class OptionsMenu(arcade.gui.UIMouseFilterMixin, arcade.gui.UIAnchorLayout):
    def __init__(
        self,
        parent_manager: arcade.gui.UIManager,
        dropdown_options: list[str],
        backgound_child: arcade.gui.UIWidget,
    ) -> None:
        super().__init__(size_hint=(1, 1))
        self.parent_manager = parent_manager
        self.background_child = backgound_child

        # Setup frame which will act like the window.
        frame = self.add(arcade.gui.UIAnchorLayout(width=800, height=700, size_hint=None))
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
        title_label_space = arcade.gui.UISpace(height=30)

        on_texture = arcade.load_texture(constants.ASSETS_DIR / "button_texture.png")
        off_texture = arcade.load_texture(constants.ASSETS_DIR / "solid_black.png")

        # Create dropdown with a specified default.
        dropdown = arcade.gui.UIDropdown(
            default=dropdown_options[0], options=dropdown_options, height=20, width=250
        )

        title_layout = arcade.gui.UIBoxLayout(align="center", space_between=50)
        title_layout.add(title_label_space)
        title_layout.add(title_label)

        back_button_layout = arcade.gui.UIAnchorLayout()
        back_button_layout.add(back_button, anchor_x="center", anchor_y="bottom", align_y=100)

        widget_layout = arcade.gui.UIBoxLayout(align="left", space_between=10)
        toggle = arcade.gui.UITextureToggle(
            on_texture=on_texture, off_texture=off_texture, width=30, height=30
        )
        self.vsync_toggle = OptionEntryContainer(
            "V-Sync", option_state_label="Disabled", component=toggle, value=True
        )
        widget_layout.add(self.vsync_toggle)

        dropdown_entry = OptionEntryContainer("Sus", option_state_label="Sus", component=dropdown)
        widget_layout.add(dropdown_entry)

        frame.add(child=title_layout, anchor_x="center_x", anchor_y="top")
        frame.add(child=widget_layout, anchor_x="left", align_x=100, align_y=120)
        frame.add(child=back_button_layout, align_y=0)

    def setup_from_dict(self) -> None:
        settings: dict[str, typing.Any] = self.load_saved_settings()

        for key, value in settings.items():
            attr = self.__getattribute__(key)

            if key.endswith("_toggle"):
                attr.value = value

    def load_saved_settings(self) -> typing.Any:
        with open(constants.SETTINGS_DIR / "saved_settings.json") as f:
            data = json.load(f)
        return data

    def on_click_back_button(self, _: arcade.gui.UIOnClickEvent) -> None:
        # Removes the widget from the manager.
        # After this the manager will respond to its events like it previously did.
        self.parent_manager.remove(self)
        self.parent_manager.remove(self.background_child)
