# NothingSupportUI Available components [AndroidViewLib:16.0.1]
* 文档生成于2025年5月2日 *
---

## Table of contents

- [Avatar](#avatar)
- [Snackbar](#snackbar)
- [Button](#button)
- [List](#list)
- [Toggle](#toggle)
- [ImageSelection](#imageselection)
- [NTTopAppBar](#nttopappbar)
- [NtBottomSheet](#ntbottomsheet)
- [NtBadge](#ntbadge)
- [NtPopupMenu](#ntpopupmenu)
- [NtTextField](#nttextfield)
- [NtSearchBar](#ntsearchbar)
- [NtDialog](#ntdialog)

---

## Avatar

### NtTextAvatarView

**XML Sample：**

```xml
<com.nothing.widget.ui.NtTextAvatarView
    android:id="@+id/v_avatar"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    app:avatar_style="primary"
    app:avatar_sze="large"
    app:text="K"
    app:nt_dot="true"/>
```

**Public Methods：**

| Parameters | Description | Default value |
|------------|-------------|---------------|
| `applySize(size: AvatarSize)` | Set the size of the avatar view | N/A |
| `setNameText(name: String, isNDot: Boolean)` | Set the name and if need to apply ndot style | N/A |

---

### NtImageAvatarView

**XML Sample：**

```xml
<com.nothing.widget.ui.NtImageAvatarView
    android:id="@+id/v_avatar"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    app:avatar_style="primary"
    app:avatar_sze="large"
    app:imageRes="@drawable/R.drawable.ic_avatar"
    app:imageUri="https://lh3.googleusercontent.com/a-/AOh14Gh2s8Sg8oM2qDVbljOJ5VMUkNHjRTWv3pIBSOIfGw=k-s256"/>
```

**Public Methods：**

| Parameters | Description | Default value |
|------------|-------------|---------------|
| `applySize(size: AvatarSize)` | Set the size of the avatar view | N/A |
| `setImageDrawable(drawable: Drawable)` | Set the drawable to be avatar icon | N/A |
| `setImageUri(uri: String)` | Set the uri to load the picture for avatar icon | N/A |

> **Note:** `ImageUri` has higher priority than `imageRes`

---

### NtAvatarView Attributes

```xml
<declare-styleable name="NtAvatarView">
    <attr name="avatar_style" format="enum">
        <enum name="primary" value="0"/>
        <enum name="secondary" value="1"/>
    </attr>
    <attr name="avatar_size" format="enum">
        <enum name="small" value="0"/>
        <enum name="medium" value="1"/>
        <enum name="large" value="2"/>
    </attr>
    <attr name="imageRes" />
    <attr name="imageUri" />
    <attr name="nt_dot" format="boolean" />
    <attr name="text" format="string" />
</declare-styleable>
```

```kotlin
enum class AvatarStyle { PRIMARY, SECONDARY }
enum class AvatarSize { SMALL, MEDIUM, LARGE }
```

---

## Snackbar

### NtSnack.Builder

Represents a snackbar.

**Sample：**

```kotlin
val ntSnackbar = NtSnackbar.Builder(parentView)
    .setMessage("Message")
    .setDuration(NtSnackbar.LENGTH_SHORT)
    .setAction("Action") { undoAction() }
    .setDismissButton(true)
    .setGravity(Gravity.BOTTOM)
    .make()
ntSnackbar.show()
ntSnackbar.dismiss()
```

**Parameters：**

| Parameters | Description | Default value |
|------------|-------------|---------------|
| `parentView` | The view to which the snackbar will be attached | N/A |
| `setMessage(String)` | Sets the message text to be displayed in the snackbar. | N/A |
| `setDuration(Int)` | Sets how long the snackbar should be shown. You can use one of the predefined constants:<br>• `LENGTH_SHORT` = 2000 (equivalent to `Toast.LENGTH_SHORT`)<br>• `LENGTH_LONG` = 3500 (equivalent to `Toast.LENGTH_LONG`)<br>• `LENGTH_FOREVER` = -1 (stays visible until manually dismissed) | `LENGTH_SHORT` |
| `setAction(String, () -> Unit)` | Adds an action button with a label and a click listener. | N/A |
| `setDismissButton(Boolean)` | Whether to show a dismiss (close) button on the snackbar. | `false` |
| `setGravity(Int)` | Sets the vertical position of the snackbar, e.g., `Gravity.BOTTOM`. | `Gravity.BOTTOM` |

---

## Button

### NtButton

- **NtStyle:** Filled
- **NtSize:** Large

**XML Sample：**

```xml
<com.nothing.widget.ui.NtButton
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    app:ntDrawable="@drawable/ic_demo"
    app:ntText="Large with icon"
    app:ntSize="large"
    app:ntStyle="filled" />
```

**Kotlin Sample：**

```kotlin
NtButton(context).apply {
    layoutParams = LinearLayout.LayoutParams(
        ViewGroup.LayoutParams.WRAP_CONTENT,
        ViewGroup.LayoutParams.WRAP_CONTENT
    ).apply {
        gravity = Gravity.CENTER_HORIZONTAL
    }
    setNtDrawable(R.drawable.ic_demo)
    setNtText("Set Button Text")
    setNtSize(NtButton.NtSize.MEDIUM)
    setNtStyle(NtButton.NtStyle.FILLED)
}
```

**Public Methods：**

| Parameters | Description | Default value |
|------------|-------------|---------------|
| `setNtDrawable(Drawable)` | Sets the drawable icon to be displayed inside the button. | N/A |
| `setNtText(String)` | Sets the text that will be displayed on the button. | N/A |
| `setNtSize(NtSize)` | Set the NT size of this button. | N/A |
| `setNtStyle(NtStyle)` | Set the NT style of this button. | N/A |

---

### NtStyle

Represents the style of the NtButton.

```xml
<attr name="ntStyle" format="enum">
    <enum name="text" value="0"/>
    <enum name="outlined" value="1"/>
    <enum name="filled" value="2"/>
</attr>
```

```kotlin
enum class NtStyle { TEXT, OUTLINED, FILLED }
```

---

### NtSize

Represents the size of the NtButton.

```xml
<attr name="ntSize" format="enum">
    <enum name="small" value="0"/>
    <enum name="medium" value="1"/>
    <enum name="large" value="2"/>
</attr>
```

```kotlin
enum class NtSize { SMALL, MEDIUM, LARGE }
```

---

## List

### NtList

A drop-in replacement for `RecyclerView` that simplifies list creation using `NtListModel` and `NtListItemModel`.

**Built-in support for:**
- Drag-and-drop to reorder items (if `draggable` is `true`)
- Swipe-to-delete to remove items (if `deletable` is `true`)

Handles item touch gestures internally, no need to manually implement `ItemTouchHelper`.

---

### NtListAdapter

`NtListAdapter` is a custom adapter that extends `ListAdapter<NtListItemModel, RecyclerView.ViewHolder>`, optimized for use with `NtList`.

**Description：**
- Uses `DiffUtil` internally for efficient item comparison and UI updates.
- Accepts a full list of items and automatically handles internal filtering and rendering using a submitList, typically derived from `NtListModel`.
- Provides a listener interface `OnItemEvent` to handle item interactions such as click, toggle, delete, and move.

---

### OnItemEvent

```kotlin
interface OnItemEvent {
    fun onItemClicked(item: NtListItemModel, position: Int)
    fun onItemActionChanged(item: NtListItemModel, position: Int, isChecked: Boolean)
    fun onItemDeleted(item: NtListItemModel, position: Int)
    fun onItemMoved(item: NtListItemModel, fromPosition: Int, toPosition: Int)
}
```

#### onItemClicked

Called when an item is tapped.

| Parameters | Description | Default value |
|------------|-------------|---------------|
| `item: NtListItemModel` | The clicked item model. | N/A |
| `position: Int` | The position of the item in the adapter. | N/A |

#### onItemActionChanged

Called when a component (Switch, Checkbox, Radio) changes state.

| Parameters | Description | Default value |
|------------|-------------|---------------|
| `item: NtListItemModel` | The clicked item model. | N/A |
| `position: Int` | The position of the item in the adapter. | N/A |
| `isChecked: Boolean` | The new checked state of the component. | N/A |

#### onItemDeleted

Called when an item is swiped and removed.

| Parameters | Description | Default value |
|------------|-------------|---------------|
| `item: NtListItemModel` | The clicked item model. | N/A |
| `position: Int` | The position of the item in the adapter. | N/A |

#### onItemMoved

Called when an item is reordered via drag-and-drop.

| Parameters | Description | Default value |
|------------|-------------|---------------|
| `item: NtListItemModel` | The clicked item model. | N/A |
| `fromPosition: Int` | The original position of the item before the move. | N/A |
| `toPosition: Int` | The new position of the item after the move. | N/A |

---

### NtListModel

Represents the content of a list.

```kotlin
data class NtListModel(
    val list: List<NtListItemModel>,
)
```

| Parameters | Description | Default value |
|------------|-------------|---------------|
| `list: List<NtListItemModel>` | List items. A data model that represents a list of `NtListItemModel`. | N/A |

**Parameters：**
- `list`: A list of `NtListItemModel` objects, which can represent different item types in the list.
  - Example value: `[NtListItemModel.NtListHeaderModel, NtListItemModel.NtNormalListItemModel]`

---

### NtListItemModel

Represents the content of a list item.

```kotlin
sealed class NtListItemModel(
    open val id: String,
)
```

| Parameters | Description | Default value |
|------------|-------------|---------------|
| `id: String` | Id of the list item. | N/A |

---

### NtListHeaderModel

Represents the header of a list group.

```kotlin
data class NtListHeaderModel(
    override val id: String,
    val text: String,
) : NtListItemModel(id = text)
```

| Parameters | Description | Default value |
|------------|-------------|---------------|
| `id: String` | Id of the list item. | N/A |
| `text: String` | The text displayed in the header. | N/A |

---

### NtListDescriptionModel

Represents the description of a list group.

```kotlin
data class NtListDescriptionModel(
    override val id: String,
    val text: String,
) : NtListItemModel(text)
```

| Parameters | Description | Default value |
|------------|-------------|---------------|
| `id: String` | Id of the list item. | N/A |
| `text: String` | The text displayed in the description. | N/A |

---

### NtListDividerModel

Represents a divider of a list group. If a list group has no header, add a divider to separate two list groups.

```kotlin
data class NtListDividerModel(
    private val dividerId: String
) : NtListItemModel("invisible${HALF_SURROGATE}divider$dividerId")
```

| Parameters | Description | Default value |
|------------|-------------|---------------|
| `dividerId: String` | The unique id of the divider | N/A |

---

### NtBaseListItemModel

An abstract base class for items that contain a headline, description, and other properties like icons and interactivity.

```kotlin
open class NtBaseListItemModel(
    override val id: String,
    open val headline: String,
    open val description: String,
    @DrawableRes open val leadingIcon: Int,
    @DrawableRes open val leadingAvatar: Int,
    open val clickable: Boolean,
    open val deletable: Boolean,
    open val draggable: Boolean,
    open val leadingDrawableTint: Int = R.color.color_icon_primary,
) : NtListItemModel(id)
```

| Parameters | Description | Default value |
|------------|-------------|---------------|
| `id: String` | Id of the list item. | N/A |
| `headline: String` | Headline of the list item. | N/A |
| `description: String` | Description of the list item. | `""` |
| `leadingIcon: Int` | Leading icon drawable, where 0 indicates no icon is displayed. | N/A |
| `leadingAvatar: Int` | Leading avatar drawable, where 0 indicates no icon is displayed. | N/A |
| `clickable: Boolean` | Controls the clickable state of this list item. | `true` |
| `deletable: Boolean` | Flag that controls whether the item supports delete actions, such as swipe-to-delete. | `true` |
| `draggable: Boolean` | Flag that controls whether the item supports drag-and-drop reordering within the list. | `false` |
| `leadingDrawableTint: Boolean` | Leading drawable tint. | `R.color.color_icon_primary` |

---

### NtNormalListItemModel

A specific type of `NtBaseListItemModel` that represents a normal list item.

```kotlin
data class NtNormalListItemModel(
    override val id: String,
    override val headline: String,
    override val description: String = "",
    @DrawableRes override val leadingIcon: Int = 0,
    @DrawableRes override val leadingAvatar: Int = 0,
    override val clickable: Boolean = true,
    override val deletable: Boolean = true,
    override val draggable: Boolean = false,
    @ColorRes override val leadingDrawableTint: Int = R.color.color_icon_primary,
) : NtBaseListItemModel(
    id = id,
    headline = headline,
    description = description,
    leadingIcon = leadingIcon,
    leadingAvatar = leadingAvatar,
    clickable = clickable,
    deletable = deletable,
    draggable = draggable,
    leadingDrawableTint = leadingDrawableTint,
)
```

---

### NtCheckboxListItemModel

A specific type of `NtBaseListItemModel` for items that have a checkbox.

```kotlin
data class NtCheckboxListItemModel(
    override val id: String,
    override val headline: String,
    override val description: String = "",
    @DrawableRes override val leadingIcon: Int = 0,
    @DrawableRes override val leadingAvatar: Int = 0,
    override val clickable: Boolean = true,
    val checked: Boolean,
    override val deletable: Boolean = true,
    override val draggable: Boolean = false,
    @ColorRes override val leadingDrawableTint: Int = R.color.color_icon_primary,
) : NtBaseListItemModel(
    id = id,
    headline = headline,
    description = description,
    leadingIcon = leadingIcon,
    leadingAvatar = leadingAvatar,
    clickable = clickable,
    deletable = deletable,
    draggable = draggable,
    leadingDrawableTint = leadingDrawableTint,
)
```

| Parameters | Description | Default value |
|------------|-------------|---------------|
| `checked: Boolean` | Boolean value indicating if the checkbox is checked. | N/A |

---

### NtRadioButtonListItemModel

A specific type of `NtBaseListItemModel` for items with a radio button.

```kotlin
data class NtRadioButtonListItemModel(
    override val id: String,
    override val headline: String,
    override val description: String = "",
    @DrawableRes override val leadingIcon: Int = 0,
    @DrawableRes override val leadingAvatar: Int = 0,
    override val clickable: Boolean = true,
    val selected: Boolean,
    override val deletable: Boolean = true,
    override val draggable: Boolean = false,
    @ColorRes override val leadingDrawableTint: Int = R.color.color_icon_primary,
) : NtBaseListItemModel(
    id = id,
    headline = headline,
    description = description,
    leadingIcon = leadingIcon,
    leadingAvatar = leadingAvatar,
    clickable = clickable,
    deletable = deletable,
    draggable = draggable,
    leadingDrawableTint = leadingDrawableTint,
)
```

| Parameters | Description | Default value |
|------------|-------------|---------------|
| `selected: Boolean` | Boolean value indicating if the radio button is selected. | N/A |

---

### NtSwitchListItemModel

A specific type of `NtBaseListItemModel` for items with a switch.

```kotlin
data class NtSwitchListItemModel(
    override val id: String,
    override val headline: String,
    override val description: String = "",
    @DrawableRes override val leadingIcon: Int = 0,
    @DrawableRes override val leadingAvatar: Int = 0,
    override val clickable: Boolean = true,
    val checked: Boolean,
    override val deletable: Boolean = true,
    override val draggable: Boolean = false,
    @ColorRes override val leadingDrawableTint: Int = R.color.color_icon_primary,
) : NtBaseListItemModel(
    id = id,
    headline = headline,
    description = description,
    leadingIcon = leadingIcon,
    leadingAvatar = leadingAvatar,
    clickable = clickable,
    deletable = deletable,
    draggable = draggable,
    leadingDrawableTint = leadingDrawableTint,
)
```

| Parameters | Description | Default value |
|------------|-------------|---------------|
| `checked: Boolean` | Boolean value indicating if the switch is in the checked state. | N/A |

---

### NtLabelChevronListItemModel

A specific type of `NtBaseListItemModel` that includes a label and a chevron (e.g., an arrow icon indicating more information).

```kotlin
data class NtLabelChevronListItemModel(
    override val id: String,
    override val headline: String,
    override val description: String = "",
    @DrawableRes override val leadingIcon: Int = 0,
    @DrawableRes override val leadingAvatar: Int = 0,
    override val clickable: Boolean = true,
    val chevronInfo: NtLabelChevronInfo,
    override val deletable: Boolean = true,
    override val draggable: Boolean = false,
    @ColorRes override val leadingDrawableTint: Int = R.color.color_icon_primary,
) : NtBaseListItemModel(
    id = id,
    headline = headline,
    description = description,
    leadingIcon = leadingIcon,
    leadingAvatar = leadingAvatar,
    clickable = clickable,
    deletable = deletable,
    draggable = draggable,
    leadingDrawableTint = leadingDrawableTint,
)
```

| Parameters | Description | Default value |
|------------|-------------|---------------|
| `chevronInfo: NtLabelChevronInfo` | An object of type `NtLabelChevronInfo` that holds information about the chevron, like whether it has a red dot and the text. | N/A |

---

### NtLabelChevronInfo

Represents information about the chevron, including whether it has a red dot and the accompanying text.

```kotlin
data class NtLabelChevronInfo(
    val hasRedDot: Boolean = true,
    val text: String = "",
)
```

| Parameters | Description | Default value |
|------------|-------------|---------------|
| `hasRedDot: Boolean` | Boolean indicating if the chevron should have a red dot. | `true` |
| `text: String` | The text that accompanies the chevron. | N/A |

---

### Sample Code

```kotlin
// Mock List Data
fun getMockList(): NtListModel {
    val result = mutableListOf<NtListItemModel>()
    var draggable = true
    val list1 = mutableListOf(
        NtListItemModel.NtListHeaderModel(
            id = "List header1",
            text = "List header"
        ),
        NtListItemModel.NtNormalListItemModel(
            id = "List1 Item1",
            headline = "List item",
            leadingIcon = R.drawable.ic_info,
            draggable = draggable,
        ),
        NtListItemModel.NtCheckboxListItemModel(
            id = "List1 Item2",
            headline = "List item",
            checked = true,
            draggable = draggable,
        ),
        NtListItemModel.NtRadioButtonListItemModel(
            id = "List1 Item3",
            headline = "List item",
            selected = true,
            draggable = draggable,
        ),
        NtListItemModel.NtSwitchListItemModel(
            id = "List1 Item4",
            headline = "List item",
            draggable = draggable,
        ),
        NtListItemModel.NtLabelChevronListItemModel(
            id = "List1 Item5",
            headline = "List item",
            chevronInfo = NtLabelChevronInfo(text = "Label"),
            draggable = draggable,
        ),
        NtListItemModel.NtListDescriptionModel(
            id = "list-2line",
            text = "list-2line"
        )
    )
    result.addAll(list1)
    return NtListModel(list = result)
}

// Main
var ntListView = findViewById<NtList>(R.id.recyclerView) // NtList
var ntAdapter = NtListAdapter()
ntListView?.adapter = ntAdapter
ntAdapter.submitList(getMockList())
ntAdapter.setOnItemEventListener(object : OnItemEvent {
    override fun onItemClicked(item: NtListItemModel, position: Int) {
        Log.d(TAG, "onItemClicked: $item, $position")
    }
    override fun onItemActionChanged(item: NtListItemModel, position: Int, isChecked: Boolean) {
        Log.d(TAG, "onItemActionChanged: $item, $position $isChecked")
    }
    override fun onItemDeleted(item: NtListItemModel, position: Int) {
        Log.d(TAG, "onItemDeleted: $item, $position")
    }
    override fun onItemMoved(item: NtListItemModel, fromPosition: Int, toPosition: Int) {
        Log.d(TAG, "onItemMoved: $item, from:$fromPosition, to:$toPosition")
    }
})
```

---

## Toggle

### NtSwitch

```kotlin
class NtSwitch @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = android.R.attr.switchStyle
) : CompoundButton(context, attrs, defStyleAttr)
```

**XML Sample：**

```xml
<com.nothing.widget.ui.NtSwitch
    android:id="@+id/switchView"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content" />
```

---

### CheckBox

#### NtCheckBox

```kotlin
open class NtCheckBox @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = android.R.attr.checkboxStyle
) : androidx.appcompat.widget.AppCompatCheckBox (context, attrs, defStyleAttr)
```

**XML Sample：**

```xml
<com.nothing.widget.ui.NtCheckBox
    android:id="@+id/selection_btn"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:layout_gravity="top|right"
    android:layout_marginTop="@dimen/layout_padding_3xs"
    android:layout_marginRight="@dimen/layout_padding_3xs"
    android:visibility="invisible"
    android:clickable="false"
    app:circleStyle="true"
    app:outlineColor="@color/color_border_lighter"/>
```

| Parameters | Description |
|------------|-------------|
| `app:circleStyle` | Controls whether the checkbox displays round samples |
| `app:outlineColor` | Controls the color of the outer frame when the checkbox is not selected |

---

### RadioButton

#### NtRadioButton

```kotlin
class NtRadioButton @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = androidx.appcompat.R.attr.radioButtonStyle
) : AppCompatRadioButton(context, attrs, defStyleAttr)
```

**XML Sample：**

```xml
<com.nothing.widget.ui.NtRadioButton
    android:id="@+id/radioButton"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content" />
```

---

## ImageSelection

### NtCheckableImage

```kotlin
class NtCheckableImage @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet?= null,
    defStyle: Int = 0
) : FrameLayout(context, attrs, defStyle)
```

**XML Sample：**

```xml
<com.nothing.widget.ui.NtCheckableImage
    android:id="@+id/nt_img_selection1"
    android:layout_width="135.9dp"
    android:layout_height="136dp"
    app:imageRes="@drawable/image_selection_demo"
```

| Parameters | Description |
|------------|-------------|
| `app:imageRes` | Image from resource |
| `app:imageUri` | Image from Uri |
| `isSelected` | Null: Not in selection mode<br>False: In selection mode and not selected<br>True: In selection mode and selected |

---

## NTTopAppBar

`NTTopNavigationBar` is a full-screen container that allows you to add views dynamically via its API. These added views become scrollable within the container. You can define the navigation bar's title directly in XML.

There are four types of `NTTopNavigationBar`, and you must specify the desired type in your layout XML.

Additionally, you can configure the visibility of the back button and other menu items via XML attributes. By implementing the corresponding interface, you can define custom actions for these items.

### Xml Attributes

| Parameters | Description |
|------------|-------------|
| `app:isOnTop <boolean>` | Default `true`. If the parameter is true, the widget will be scrollable. If false, widget become unscrollable. |
| `app:scrollable <boolean>` | Defaults to `true`. When enabled, NTTopNavigation is scrollable; otherwise, it is fixed. |
| `app:includeAdditionalSpace <boolean>` | Defaults to `false`. When enabled, the additional space is shown; otherwise, it is hidden. |
| `app:type` | There are 4 types for NTTopNavigationBar: `general`, `small`, `medium`, `large`. The actual UI style, you can reference Sample Application |
| `app:leadingIconRes` | App should set icon drawable |
| `trail_icon_<1-3>_Res` | App should set icon drawable |
| `title` | Set the string on the widget |

### XML Layout Setting

The layout needs use `NestedScrollView` as second level, and set attribute `app:layout_behavior=@string/appbar_scrolling_view_behavior`

Then add the customize layout under `NestedScrollView`.

**Sample code as below：**

```xml
<?xml version="1.0" encoding="utf-8"?>
<com.nothing.widget.ui.NtTopAppBar
    xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    android:id="@+id/borderTopAppBar"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    app:leadingIconRes="@drawable/ic_back_arrow"
    android:background="@color/main_color"
    app:title="Border"
    app:type="medium"
    app:includeAdditionalSpace="true">
    <androidx.core.widget.NestedScrollView
        android:layout_width="match_parent"
        android:layout_height="match_parent"
        android:scrollbars="none"
        android:paddingTop="68dp"
        android:paddingStart="@dimen/layout_margin_default"
        android:paddingEnd="@dimen/layout_margin_default"
        app:layout_behavior="@string/appbar_scrolling_view_behavior">
        <!-- add customize view at here -->
    </androidx.core.widget.NestedScrollView>
</com.nothing.widget.ui.NtTopAppBar>
```

### Public methods

| Parameters | Description | Default value |
|------------|-------------|---------------|
| `setTrailIconDescription(index: TrailIconIndex, desc: String)` | Use `setContentDescription` for trail icon. `TrailIconIndex` is a public enum in `NtTopAppBar`. | N/A |
| `setLeadingIconDescription(desc: String)` | Use `setContentDescription` for leading icon. | N/A |
| `setTrailButtons(buttons: List<NtPopupMenuModel>)` | Use `setTrailButtons` to set trail buttons. Trail button will display the icon first, without icon will be displayed as text button, more than 3 will be combined into more menu. | N/A |

### Receive click event

The widget needs developer to inflate view then set it as content.

**Sample code as below：**

```kotlin
override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    setContentView(R.layout.lib_view_top_navigation_bar_layout)
    var view: NtTopAppBar? = findViewById<NtTopAppBar>(R.id.ntTopAppBar)
    view?.setClickListener(object : NtTopAppBar.ClickListener {
        override fun onLeadingIconClicked() {
        }
        override fun onTrailIcon1Clicked() {
        }
        override fun onTrailIcon2Clicked() {
        }
        override fun onTrailIcon3Clicked() {
        }
    })
}
```

### setTrailButtons

```kotlin
var topAppBar: NtTopAppBar? = findViewById<NtTopAppBar>(R.id.ntTopAppBar)
val itemModels = mutableListOf<NtPopupMenuModel>()
itemModels.add(
    // trail icon
    NtPopupMenuModel(
        icon = R.drawable.ic_info,
        text = "Info icon",
        desc = "Info icon"
    ) {
        // click action
    }
)
itemModels.add(
    // text action button
    NtPopupMenuModel(
        text = "Action button",
        desc = "Action button"
    ) {
        // click action
    }
)
topAppBar.setTrailButtons(itemsModel)
```

---

## NtBottomSheet

```kotlin
class NtBottomSheet(
    context: Context,
) : BottomSheetDialog(context, WidgetR.style.NtBottomSheetDialogTheme) {}
```

**Sample：**

```kotlin
val bottomSheet = NtBottomSheet(context)
bottomSheet.setContent("This is bottom sheet description. This is bottom sheet description. This is bottom sheet description.")
bottomSheet.setAnnotation("This is annotation and is optional.")
bottomSheet.setPositiveButton("Positive") {
    Toast.makeText(context, "Positive button clicked", Toast.LENGTH_SHORT).show()
}
bottomSheet.show()
```

### Public methods

| Parameters | Description | Default value |
|------------|-------------|---------------|
| `setTopImage(imageResId: Int, imageSize: ImageSize = ImageSize.SMALL)` | Use `setTopImage` to set the image resource on top of bottom sheet | The default image size is small. |
| `setTopImage(drawable: Drawable, imageSize: ImageSize = ImageSize.SMALL)` | Use `setTopImage` to set the image drawable on top of bottom sheet | The default image size is small. |
| `setLeadingControl(text: String = "", imageResId: Int = 0, listener: () -> Unit)` | Use `setLeadingControl` for leading icon | N/A |
| `setTrailingControl(text: String = "", imageResId: Int = 0, listener: () -> Unit)` | Use `setTrailingControl` for trailing icon | N/A |
| `setTitle(title: String)` | Use `setTitle` to set the title text on top of bottom sheet | N/A |
| `setContent(content: String)` | Use `setContent` to set the content text on middle of bottom sheet | N/A |
| `setAnnotation(annotation: String)` | Use `setAnnotation` to set the annotation text on bottom of bottom sheet content. | N/A |
| `setPositiveButton(text: String, listener: () -> Unit)` | Use `setPositiveButton` to set the positive button on the bottom sheet. | N/A |
| `setNegativeButton(text: String, listener: () -> Unit)` | Use `setNegativeButton` to set the negative button on the bottom sheet. | N/A |
| `setButtonTextAllCaps(enabled: Boolean)` | Use `setButtonTextAllCaps` to make the positive and negative button text all caps | N/A |

---

## NtBadge

```kotlin
class NtBadge @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : androidx.appcompat.widget.AppCompatImageView(context, attrs, defStyleAttr){}
```

**XML Sample：**

```xml
<com.nothing.widget.ui.NtBadge
    android:id="@+id/red_dot"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:layout_marginEnd="@dimen/layout_padding_xs"
    app:layout_constraintBottom_toBottomOf="parent"
    app:layout_constraintEnd_toStartOf="@+id/trailingLabel"
    app:layout_constraintTop_toTopOf="parent" />
```

---

## NtPopupMenu

```kotlin
class NtPopupMenu @JvmOverloads constructor(
    private val context: Context,
    itemModels: List<NtPopupMenuModel>
) : PopupWindow(context) {}
```

**Sample：**

```kotlin
private val menuItemWithoutIcon = NtPopupMenuModel(icon = 0, text = "Menu item", onClick = {})
private val menuItemWithIcon = NtPopupMenuModel(icon = R.drawable.ic_info, text = "Menu item", onClick = {})
private val itemModels = mutableListOf<NtPopupMenuModel>(menuItemWithoutIcon)

val popupMenu = NtPopupMenu(
    context = this@LibViewMenuActivity,
    itemModels = itemModels
).apply {
    setOnDismissListener(object : PopupWindow.OnDismissListener {
        override fun onDismiss() {
            topAppBar.trailMenuExpanded(false, anchor)
        }
    })
    show(anchor)
}
```

---

## NtTextField

```kotlin
class NtTextField @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = android.R.attr.editTextStyle
) : LinearLayout(context, attrs, defStyleAttr), View.OnClickListener {}
```

**XML Sample：**

```xml
<com.nothing.widget.ui.NtTextField
    android:id="@+id/without_icon_text_field"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:inputType="number"
    android:hint="Please enter 6 digits" />
```

### Public methods

| Parameters | Description | Default value |
|------------|-------------|---------------|
| `setText(text: CharSequence?)` | Use `setText` to set the content in the text field | N/A |
| `setHint(hint: CharSequence?)` | Use `setHint` to set the hint in the text field | N/A |
| `setError(error: CharSequence?)` | Use `setError` to set the remind message under the text field | N/A |
| `setDrawable(component: Component, drawableRes: Int)` | Use `setDrawable` to set the drawable resource for the leading icon or trailing icon.<br>`Component.LEADING_ICON`<br>`Component.TRAILING_ICON` | N/A |
| `setContentDescription(contentDescription: String, component: Component)` | Use `setContentDescription` to set the description.<br>`Component.LEADING_ICON`<br>`Component.TRAILING_ICON`<br>`Component.INPUT_FIELD` | N/A |
| `setClickListener(listener: ClickListener)` | `ClickListener` will callback when trailing icon click | N/A |

---

## NtSearchBar

```kotlin
class NtSearchBar @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = android.R.attr.editTextStyle
) : LinearLayout(context, attrs, defStyleAttr), View.OnClickListener {}
```

**XML Sample：**

```xml
<com.nothing.widget.ui.NtSearchBar
    android:id="@+id/search_bar"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:paddingBottom="16dp"
    android:paddingTop="68dp"
    android:inputType="text"
    app:leadingIconRes="@drawable/ic_back_arrow"
    app:trailingIconRes="@drawable/ic_more"
    android:hint="This is sample text" />
```

### Interface

```kotlin
interface ClickListener {
    fun onLeadingIconClicked()
    fun onSearchIconClicked()
    fun onTrailingIconClicked()
    fun onCleanIconClicked()
}
```

### Public methods

| Parameters | Description | Default value |
|------------|-------------|---------------|
| `setText(text: CharSequence?)` | Use `setText` to set the content in the text field | N/A |
| `setHint(hint: CharSequence?)` | Use `setHint` to set the hint in the text field | N/A |
| `setError(error: CharSequence?)` | Use `setError` to set the remind message under the text field | N/A |
| `setDrawable(component: Component, drawableRes: Int)` | Use `setDrawable` to set the drawable resource for the leading icon or trailing icon.<br>`Component.LEADING_ICON`<br>`Component.TRAILING_ICON` | N/A |
| `setContentDescription(contentDescription: String, component: Component)` | Use `setContentDescription` to set the description.<br>`Component.LEADING_ICON`<br>`Component.TRAILING_ICON`<br>`Component.SEARCH_ICON`<br>`Component.CLEAN_ICON`<br>`Component.INPUT_FIELD` | N/A |
| `setClickListener(listener: ClickListener)` | `ClickListener` will callback when each icon click | N/A |
| `setDismissListener(listener: DialogInterface.OnDismissListener)` | Use set to dialog `setDismissListener` | N/A |
| `setCancelable(flag: Boolean)` | Use set to dialog `setCancelable` | N/A |
| `setCanceledOnTouchOutside(cancel: Boolean)` | Use set to dialog `setCanceledOnTouchOutside` | N/A |
| `getDialog()` | Return the alert dialog instance | N/A |
| `setCustomView(view: View?)` | Use to set custom view to dialog content. The text content view will hide after set custom view | N/A |
| `updateButtons(infos: List<NtDialogButtonInfo>)` | Use to update button state. | N/A |

---

## NtDialog

```kotlin
class NtDialog(
    private var context: Context,
    buttons: List<NtDialogButtonInfo> = emptyList(),
    verticalButtons: Boolean = false
) : DialogInterface.OnCancelListener {}
```

**Sample：**

```kotlin
val firstButton = NtDialogButtonInfo(
    label = "Label 1",
    onClick = {},
    style = NtDialogButtonStyle.Warning)
var middleButton = NtDialogButtonInfo(
    label = "Label 2",
    onClick = {},
    style = NtDialogButtonStyle.Normal)
var endButton = NtDialogButtonInfo(
    label = "Label 3",
    onClick = {},
    style = NtDialogButtonStyle.Normal)
var buttons = listOf(
    endButton,
    middleButton,
    firstButton)
val dialog = NtDialog(context, buttons, verticalButtons)
dialog.setContent(content)
dialog.show()
```

### Public methods

| Parameters | Description | Default value |
|------------|-------------|---------------|
| `setTitle(title: String)` | Use `setTitle` to set the title text on top of dialog | N/A |
| `setContent(content: String)` | Use `setContent` to set the content text in the dialog | N/A |
| `setTopImage(imageResId: Int)` | Use `setTopImage` to set the image resource on top of dialog | N/A |
| `setTopImage(drawable: Drawable)` | Use `setTopImage` to set the image drawable on top of dialog | N/A |
| `setCustomView(view: View?)` | Use custom view replace default content view. | N/A |

---