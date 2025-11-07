# How to Fix the ONE Wedge Bump Offer - Add Variant Selectors

## Problem
Your ONE Wedge bump offer checkbox doesn't have variant selectors (Right Hand/Left Hand options), while the working page does.

## Solution

### Step 1: Update the Checkbox Value
Find this line in your HTML:
```html
<input type="checkbox" name="product" ... value="9783" variantvalue="" ...>
```

Change it to:
```html
<input type="checkbox" name="product" ... value="choose" variantvalue="" ...>
```

### Step 2: Add the Variant Selector After the Label
Right after the closing `</label>` tag for the checkbox (around line with `id="itr97x"`), add this HTML:

```html
<div data-secondsdelay="" class="faux-select-offer">
  <div data-text="text" data-secondsdelay="" class="faux-select-offer-selected">Select Club Type
  </div>
  <div data-secondsdelay="" class="faux-select-offer-options">
    <div data-secondsdelay="" class="faux-select-offer-option">
      <input type="checkbox" name="product" replaceproductid="" freeshipping="" coupon="" quantity="" price="" id="ip773u" value="9783" variantvalue="RIGHT_HAND_VARIANT_ID" class="fk-product-checkbox">Right Hand
    </div>
    <div data-secondsdelay="" class="faux-select-offer-option">
      <input type="checkbox" name="product" replaceproductid="" freeshipping="" coupon="" quantity="" price="" id="ig8lai" value="9783" variantvalue="LEFT_HAND_VARIANT_ID" class="fk-product-checkbox">Left Hand
    </div>
  </div>
</div>
```

### Step 3: Replace Placeholder Variant IDs
You need to replace:
- `RIGHT_HAND_VARIANT_ID` with the actual variant ID for Right Hand (product ID 9783)
- `LEFT_HAND_VARIANT_ID` with the actual variant ID for Left Hand (product ID 9783)

**To find these IDs:**
1. Check your product management system for product ID 9783
2. Look at the variant IDs for Right Hand and Left Hand options
3. Or check the working page - if it uses the same product structure, you might be able to infer the pattern

## Complete Example (Before and After)

### BEFORE (Current - Missing Variants):
```html
<label id="itr97x"><div id="iajnnk" data-secondsdelay="">
  <input type="checkbox" name="product" onclick="checkBoxChange(attributes)" requiredtype="" opencheckboxsection="" id="ibxagv" replaceproductid="" freeshipping="" quantity="" price="" coupon="" value="9783" variantvalue="" class="fk-product-checkbox">
  </div><div data-text="text" id="ivscb7" data-secondsdelay="">Yes, Please ADD The World's First Escape Wedge, Risk Free To My Order ($73). If I don't love it, I don't pay.
  </div></label>
```

### AFTER (Fixed - With Variants):
```html
<label id="itr97x"><div id="iajnnk" data-secondsdelay="">
  <input type="checkbox" name="product" onclick="checkBoxChange(attributes)" requiredtype="" opencheckboxsection="" id="ibxagv" replaceproductid="" freeshipping="" quantity="" price="" coupon="" value="choose" variantvalue="" class="fk-product-checkbox">
  </div><div data-text="text" id="ivscb7" data-secondsdelay="">Yes, Please ADD The World's First Escape Wedge, Risk Free To My Order ($73). If I don't love it, I don't pay.
  </div></label>
<div data-secondsdelay="" class="faux-select-offer">
  <div data-text="text" data-secondsdelay="" class="faux-select-offer-selected">Select Club Type
  </div>
  <div data-secondsdelay="" class="faux-select-offer-options">
    <div data-secondsdelay="" class="faux-select-offer-option">
      <input type="checkbox" name="product" replaceproductid="" freeshipping="" coupon="" quantity="" price="" id="ip773u" value="9783" variantvalue="RIGHT_HAND_VARIANT_ID" class="fk-product-checkbox">Right Hand
    </div>
    <div data-secondsdelay="" class="faux-select-offer-option">
      <input type="checkbox" name="product" replaceproductid="" freeshipping="" coupon="" quantity="" price="" id="ig8lai" value="9783" variantvalue="LEFT_HAND_VARIANT_ID" class="fk-product-checkbox">Left Hand
    </div>
  </div>
</div>
```

## Notes
- The structure matches the working page exactly
- The CSS classes (`faux-select-offer`, `faux-select-offer-selected`, `faux-select-offer-options`, `faux-select-offer-option`) should already exist in your stylesheet since they're used on the working page
- Make sure the variant IDs match your actual product configuration


