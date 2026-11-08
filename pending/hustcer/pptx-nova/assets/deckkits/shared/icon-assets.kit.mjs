// icon-assets.kit.mjs - local Tabler icon pack consumption for DeckKit generators
import { getTablerIconAsset } from '../../../scripts/lib/assets/tabler-icons.mjs'

export {
  getTablerIconAsset,
  getTablerIconPackInfo,
  getTablerIconSvg,
  hasTablerIcon,
  listTablerIconNames,
  loadTablerIcons,
  loadTablerIconSet,
  normalizeTablerIconName,
  resolveTablerIconEntry,
  resolveTablerIconName,
  searchTablerIcons,
} from '../../../scripts/lib/assets/tabler-icons.mjs'

const unit = (value) => (typeof value === 'number' && Number.isFinite(value) ? `${value}in` : value)

export function addTablerIconPicture(ops, slide, shapeName, iconName, x, y, w, h, options = {}) {
  if (!Array.isArray(ops)) {
    throw new Error('addTablerIconPicture requires an ops array')
  }
  const op = {
    op: 'add-image',
    slide,
    name: shapeName,
    x: unit(x),
    y: unit(y),
    w: unit(w),
    h: unit(h),
    ...getTablerIconAsset(iconName, options),
  }
  ops.push(op)
  return op
}
