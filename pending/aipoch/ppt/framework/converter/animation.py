# -*- coding: utf-8 -*-
"""
Animation mapping engine for HTML to PowerPoint conversion
"""

from pptx.oxml.ns import qn
from lxml import etree


# HTML preset name -> PowerPoint (preset_id, subtype)
PRESET_MAP = {
    'fadeIn': ('10', '0'),      # Fade
    'slideUp': ('2', '4'),      # Fly In from Bottom
    'slideDown': ('2', '1'),    # Fly In from Top
    'slideLeft': ('2', '8'),    # Fly In from Right
    'slideRight': ('2', '2'),   # Fly In from Left
    'scaleIn': ('23', '16'),    # Grow (from center)
    'zoomIn': ('53', '16'),     # Grow & Turn
    'flipIn': ('55', '0'),      # Swivel
    'appear': ('1', '0'),       # Appear (instant)
}

# Exit animation presets
EXIT_PRESET_MAP = {
    'fadeOut': ('10', '0'),     # Fade Out
    'slideUp': ('2', '1'),      # Fly Out to Top
    'slideDown': ('2', '4'),    # Fly Out to Bottom
    'scaleOut': ('23', '16'),   # Shrink (to center)
    'disappear': ('1', '0'),    # Disappear (instant)
}


class AnimationResolver:
    """
    Resolves animation configuration using priority:
    element.animation > slide.defaultAnimation > COMPONENT_DEFAULTS
    """
    
    def __init__(self, component_defaults: dict):
        self.component_defaults = component_defaults
    
    def resolve(self, element_data: dict, slide_data: dict = None) -> dict:
        """
        Resolve animation configuration for an element.
        
        Returns: {
            'preset': str,        # HTML preset name (e.g., 'slideUp')
            'duration': int,      # Duration in ms
            'delay': int,         # Delay in ms
            'stagger': int,       # Stagger interval in ms for list items
            'easing': str,        # CSS easing function (for reference)
        }
        """
        slide_data = slide_data or {}
        component_type = element_data.get('type', 'default')
        
        # 1. Get component default config
        component_default = self.component_defaults.get(
            component_type, 
            {'preset': 'slideUp', 'duration': 500}
        )
        
        # 2. Get slide-level default
        slide_default = slide_data.get('defaultAnimation', {})
        
        # 3. Get element-level animation config
        element_anim = element_data.get('animation', {})
        
        # Normalize string shorthand: "scaleIn" -> {"preset": "scaleIn"}
        if isinstance(element_anim, str):
            element_anim = {'preset': element_anim}
        
        # 4. Merge configs (priority: element > slide > component)
        final_config = {
            **component_default,
            **slide_default,
            **element_anim
        }
        
        # Ensure required fields exist
        return {
            'preset': final_config.get('preset', 'slideUp'),
            'duration': final_config.get('duration', 500),
            'delay': final_config.get('delay', 0),
            'stagger': final_config.get('stagger', 0),
            'easing': final_config.get('easing', 'cubic-bezier(0.4, 0, 0.2, 1)'),
        }
    
    def get_ppt_preset(self, html_preset: str, is_exit: bool = False) -> tuple:
        """
        Get PowerPoint preset ID and subtype for an HTML preset name.
        
        Returns: (preset_id: str, subtype: str)
        """
        if is_exit:
            return EXIT_PRESET_MAP.get(html_preset, EXIT_PRESET_MAP.get('fadeOut'))
        return PRESET_MAP.get(html_preset, PRESET_MAP['fadeIn'])


class AnimationBuilder:
    """
    Builds PowerPoint animation XML for entrance/exit animations.
    Handles click-triggered animation groups (step system).
    """
    
    def __init__(self, resolver: AnimationResolver):
        self.resolver = resolver
        self.anim_id = 3
        self.click_groups = {}   # step -> list of entrance animations
        self.exit_groups = {}    # step -> list of exit animations
    
    def reset(self):
        """Reset for a new slide"""
        self.anim_id = 3
        self.click_groups = {}
        self.exit_groups = {}
    
    def queue_entrance(self, shape, preset: str, step: int, 
                       delay_ms: int = 0, duration_ms: int = 500):
        """
        Queue an entrance animation for a shape.
        
        Args:
            shape: The python-pptx shape object
            preset: HTML animation preset name (e.g., 'slideUp')
            step: Step number (0 = visible on load, 1+ = click to reveal)
            delay_ms: Delay within the step for stagger effect
            duration_ms: Animation duration
        """
        if step not in self.click_groups:
            self.click_groups[step] = []
        
        self.click_groups[step].append({
            'shape': shape,
            'shape_id': shape.shape_id,
            'preset': preset,
            'is_exit': False,
            'delay': delay_ms,
            'duration': duration_ms,
        })
    
    def queue_exit(self, shape, preset: str, step: int,
                   delay_ms: int = 0, duration_ms: int = 300):
        """
        Queue an exit animation for a shape.
        
        Args:
            shape: The python-pptx shape object
            preset: HTML animation preset name (e.g., 'fadeOut')
            step: Step number at which this shape should disappear
            delay_ms: Delay within the step
            duration_ms: Animation duration
        """
        if step not in self.exit_groups:
            self.exit_groups[step] = []
        
        self.exit_groups[step].append({
            'shape': shape,
            'shape_id': shape.shape_id,
            'preset': preset,
            'is_exit': True,
            'delay': delay_ms,
            'duration': duration_ms,
        })
    
    def apply_to_slide(self, slide):
        """
        Apply all queued animations to the slide.
        Creates the timing XML structure with click-triggered groups.
        """
        if not self.click_groups and not self.exit_groups:
            return
        
        sld = slide._element
        
        # Create timing structure
        timing = self._create_timing_structure()
        sld.append(timing)
        
        ns = {'p': 'http://schemas.openxmlformats.org/presentationml/2006/main'}
        main_seq_child_lst = timing.find('.//p:seq/p:cTn/p:childTnLst', ns)
        
        # Get all steps and sort them
        all_steps = set(self.click_groups.keys()) | set(self.exit_groups.keys())
        sorted_steps = sorted([s for s in all_steps if s > 0])
        
        for step in sorted_steps:
            # Exit animations first (things disappearing)
            exit_anims = self.exit_groups.get(step, [])
            # Then entrance animations (things appearing)
            entrance_anims = self.click_groups.get(step, [])
            
            all_anims = exit_anims + entrance_anims
            
            if all_anims:
                click_group = self._create_click_group(all_anims)
                main_seq_child_lst.append(click_group)
    
    def _create_timing_structure(self):
        """Create the base timing XML structure"""
        timing_xml = '''
        <p:timing xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
            <p:tnLst>
                <p:par>
                    <p:cTn id="1" dur="indefinite" restart="never" nodeType="tmRoot">
                        <p:childTnLst>
                            <p:seq concurrent="1" nextAc="seek">
                                <p:cTn id="2" dur="indefinite" nodeType="mainSeq">
                                    <p:childTnLst/>
                                </p:cTn>
                                <p:prevCondLst>
                                    <p:cond evt="onPrev" delay="0">
                                        <p:tgtEl><p:sldTgt/></p:tgtEl>
                                    </p:cond>
                                </p:prevCondLst>
                                <p:nextCondLst>
                                    <p:cond evt="onNext" delay="0">
                                        <p:tgtEl><p:sldTgt/></p:tgtEl>
                                    </p:cond>
                                </p:nextCondLst>
                            </p:seq>
                        </p:childTnLst>
                    </p:cTn>
                </p:par>
            </p:tnLst>
        </p:timing>
        '''
        return etree.fromstring(timing_xml)
    
    def _create_click_group(self, anims: list):
        """
        Create a click-triggered animation group.
        
        IMPORTANT: In PowerPoint animation XML:
        - First animation in a click group: nodeType="clickEffect" (triggered by click)
        - Subsequent animations: nodeType="withEffect" (plays with delay from first)
        """
        # Outer par for the click group
        group_par = etree.Element(qn('p:par'))
        group_cTn = etree.SubElement(group_par, qn('p:cTn'), {
            'id': str(self.anim_id),
            'fill': 'hold'
        })
        self.anim_id += 1
        
        # Start condition: indefinite (will be triggered by click through first child)
        st_cond_lst = etree.SubElement(group_cTn, qn('p:stCondLst'))
        etree.SubElement(st_cond_lst, qn('p:cond'), {'delay': 'indefinite'})
        
        # Child animations
        child_tn_lst = etree.SubElement(group_cTn, qn('p:childTnLst'))
        
        for i, anim_data in enumerate(anims):
            is_first = (i == 0)
            anim_par = self._create_single_animation(anim_data, is_first)
            child_tn_lst.append(anim_par)
        
        return group_par
    
    def _create_single_animation(self, anim_data: dict, is_click_trigger: bool = False):
        """
        Create a single animation node.
        
        Args:
            anim_data: Animation configuration
            is_click_trigger: If True, this animation triggers on click (clickEffect)
                              If False, plays with previous animation (withEffect)
        """
        shape_id = anim_data['shape_id']
        preset = anim_data['preset']
        is_exit = anim_data['is_exit']
        delay = anim_data['delay']
        duration = anim_data['duration']
        
        # Get PowerPoint preset
        preset_id, subtype = self.resolver.get_ppt_preset(preset, is_exit)
        anim_class = 'exit' if is_exit else 'entr'
        visibility_val = 'hidden' if is_exit else 'visible'
        filter_transition = 'out' if is_exit else 'in'
        
        # nodeType determines when animation triggers
        node_type = 'clickEffect' if is_click_trigger else 'withEffect'
        
        # Build effect XML
        effect_content = self._build_effect_xml(
            shape_id, preset, is_exit, duration, filter_transition
        )
        
        anim_xml = f'''
        <p:par xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
            <p:cTn id="{self.anim_id}" presetID="{preset_id}" presetClass="{anim_class}" presetSubtype="{subtype}" fill="hold" nodeType="{node_type}">
                <p:stCondLst>
                    <p:cond delay="{delay}"/>
                </p:stCondLst>
                <p:childTnLst>
                    <p:set>
                        <p:cBhvr>
                            <p:cTn id="{self.anim_id + 1}" dur="1" fill="hold">
                                <p:stCondLst>
                                    <p:cond delay="0"/>
                                </p:stCondLst>
                            </p:cTn>
                            <p:tgtEl>
                                <p:spTgt spid="{shape_id}"/>
                            </p:tgtEl>
                            <p:attrNameLst>
                                <p:attrName>style.visibility</p:attrName>
                            </p:attrNameLst>
                        </p:cBhvr>
                        <p:to>
                            <p:strVal val="{visibility_val}"/>
                        </p:to>
                    </p:set>
                    {effect_content}
                </p:childTnLst>
            </p:cTn>
        </p:par>
        '''
        self.anim_id += 6
        return etree.fromstring(anim_xml)
    
    def _build_effect_xml(self, shape_id: int, preset: str, 
                          is_exit: bool, duration: int, transition: str) -> str:
        """Build the animation effect XML based on preset type"""
        id_base = self.anim_id + 2
        
        # Motion-based animations (fly, slide)
        if preset in ['slideUp', 'slideDown', 'slideLeft', 'slideRight']:
            return self._build_motion_effect(shape_id, preset, is_exit, duration, id_base)
        
        # Scale-based animations (zoom, scale)
        if preset in ['scaleIn', 'zoomIn', 'scaleOut']:
            return self._build_scale_effect(shape_id, is_exit, duration, id_base)
        
        # Default: fade effect
        return self._build_fade_effect(shape_id, duration, transition, id_base)
    
    def _build_fade_effect(self, shape_id: int, duration: int, 
                           transition: str, id_base: int) -> str:
        """Build fade animation effect"""
        return f'''
                    <p:animEffect transition="{transition}" filter="fade">
                        <p:cBhvr>
                            <p:cTn id="{id_base}" dur="{duration}"/>
                            <p:tgtEl>
                                <p:spTgt spid="{shape_id}"/>
                            </p:tgtEl>
                        </p:cBhvr>
                    </p:animEffect>'''
    
    def _build_motion_effect(self, shape_id: int, preset: str, 
                             is_exit: bool, duration: int, id_base: int) -> str:
        """Build motion (fly/slide) animation effect"""
        # Determine direction
        if preset == 'slideUp':
            offset = '0.15' if not is_exit else '-0.15'
            attr = 'ppt_y'
        elif preset == 'slideDown':
            offset = '-0.15' if not is_exit else '0.15'
            attr = 'ppt_y'
        elif preset == 'slideLeft':
            offset = '0.15' if not is_exit else '-0.15'
            attr = 'ppt_x'
        else:  # slideRight
            offset = '-0.15' if not is_exit else '0.15'
            attr = 'ppt_x'
        
        if is_exit:
            start_val = f'#{attr}'
            end_val = f'#{attr}+{offset}'
        else:
            start_val = f'#{attr}+{offset}'
            end_val = f'#{attr}'
        
        transition = 'out' if is_exit else 'in'
        
        return f'''
                    <p:anim calcmode="lin" valueType="num">
                        <p:cBhvr additive="base">
                            <p:cTn id="{id_base}" dur="{duration}" fill="hold"/>
                            <p:tgtEl>
                                <p:spTgt spid="{shape_id}"/>
                            </p:tgtEl>
                            <p:attrNameLst>
                                <p:attrName>{attr}</p:attrName>
                            </p:attrNameLst>
                        </p:cBhvr>
                        <p:tavLst>
                            <p:tav tm="0">
                                <p:val>
                                    <p:strVal val="{start_val}"/>
                                </p:val>
                            </p:tav>
                            <p:tav tm="100000">
                                <p:val>
                                    <p:strVal val="{end_val}"/>
                                </p:val>
                            </p:tav>
                        </p:tavLst>
                    </p:anim>
                    <p:animEffect transition="{transition}" filter="fade">
                        <p:cBhvr>
                            <p:cTn id="{id_base + 1}" dur="{duration}"/>
                            <p:tgtEl>
                                <p:spTgt spid="{shape_id}"/>
                            </p:tgtEl>
                        </p:cBhvr>
                    </p:animEffect>'''
    
    def _build_scale_effect(self, shape_id: int, is_exit: bool, 
                            duration: int, id_base: int) -> str:
        """Build scale/zoom animation effect"""
        if is_exit:
            start_w, end_w = '#ppt_w', '#ppt_w*0.7'
            start_h, end_h = '#ppt_h', '#ppt_h*0.7'
        else:
            start_w, end_w = '#ppt_w*0.7', '#ppt_w'
            start_h, end_h = '#ppt_h*0.7', '#ppt_h'
        
        transition = 'out' if is_exit else 'in'
        
        return f'''
                    <p:anim calcmode="lin" valueType="num">
                        <p:cBhvr additive="base">
                            <p:cTn id="{id_base}" dur="{duration}" fill="hold"/>
                            <p:tgtEl>
                                <p:spTgt spid="{shape_id}"/>
                            </p:tgtEl>
                            <p:attrNameLst>
                                <p:attrName>ppt_w</p:attrName>
                            </p:attrNameLst>
                        </p:cBhvr>
                        <p:tavLst>
                            <p:tav tm="0">
                                <p:val>
                                    <p:strVal val="{start_w}"/>
                                </p:val>
                            </p:tav>
                            <p:tav tm="100000">
                                <p:val>
                                    <p:strVal val="{end_w}"/>
                                </p:val>
                            </p:tav>
                        </p:tavLst>
                    </p:anim>
                    <p:anim calcmode="lin" valueType="num">
                        <p:cBhvr additive="base">
                            <p:cTn id="{id_base + 1}" dur="{duration}" fill="hold"/>
                            <p:tgtEl>
                                <p:spTgt spid="{shape_id}"/>
                            </p:tgtEl>
                            <p:attrNameLst>
                                <p:attrName>ppt_h</p:attrName>
                            </p:attrNameLst>
                        </p:cBhvr>
                        <p:tavLst>
                            <p:tav tm="0">
                                <p:val>
                                    <p:strVal val="{start_h}"/>
                                </p:val>
                            </p:tav>
                            <p:tav tm="100000">
                                <p:val>
                                    <p:strVal val="{end_h}"/>
                                </p:val>
                            </p:tav>
                        </p:tavLst>
                    </p:anim>
                    <p:animEffect transition="{transition}" filter="fade">
                        <p:cBhvr>
                            <p:cTn id="{id_base + 2}" dur="{duration}"/>
                            <p:tgtEl>
                                <p:spTgt spid="{shape_id}"/>
                            </p:tgtEl>
                        </p:cBhvr>
                    </p:animEffect>'''
